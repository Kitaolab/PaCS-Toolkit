"""
PBC treatment of an mdtraj trajectory, following the gromacs procedure

pbc_level = 1 : no treatment
pbc_level = 2 : trjconv -pbc mol
                (make molecules whole and put their center of mass in the box)
pbc_level = 3 : trjconv -center (centering atom -> box center)
                trjconv -pbc atom (put every atom in the box)
                trjconv -pbc mol

Molecules are built from the topology bonds AND the residues: all atoms in the same
residue are always kept together, even if the topology has no bonds for them
(e.g. a ligand read from .pdb/.gro without CONECT records).
"""

from collections import deque
from typing import Iterable, List, Optional, Tuple

import numpy as np


def _to_frac(xyz: np.ndarray, box: np.ndarray) -> np.ndarray:
    # xyz: (F, N, 3), box: (F, 3, 3) with box vectors as rows
    return np.einsum("fni,fij->fnj", xyz, np.linalg.inv(box))


def _to_cart(frac: np.ndarray, box: np.ndarray) -> np.ndarray:
    return np.einsum("fni,fij->fnj", frac, box)


def build_molecules(
    topology, atom_indices: Optional[Iterable[int]] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build molecules (bonds + residues) containing the given atoms.

    Returns
        atoms  : indices of all atoms in those molecules, in BFS order
        parent : parent atom of each atom in `atoms` (-1 for the root of a molecule)
        mol_id : molecule id of each atom in `atoms`
    """
    n_atoms = topology.n_atoms
    adjacency: List[List[int]] = [[] for _ in range(n_atoms)]
    for a, b in topology.bonds:
        adjacency[a.index].append(b.index)
        adjacency[b.index].append(a.index)
    # star edges inside each residue so that a residue is never split
    for residue in topology.residues:
        idx = [atom.index for atom in residue.atoms]
        for i in idx[1:]:
            adjacency[idx[0]].append(i)
            adjacency[i].append(idx[0])

    if atom_indices is None:
        seeds = range(n_atoms)
    else:
        seeds = sorted(set(int(i) for i in atom_indices))

    visited = np.zeros(n_atoms, dtype=bool)
    atoms, parent, mol_id = [], [], []
    n_mol = 0
    for seed in seeds:
        if visited[seed]:
            continue
        # the seed is the reference atom for making this molecule whole
        visited[seed] = True
        queue = deque([(seed, -1)])
        while queue:
            atom, par = queue.popleft()
            atoms.append(atom)
            parent.append(par)
            mol_id.append(n_mol)
            for nb in adjacency[atom]:
                if not visited[nb]:
                    visited[nb] = True
                    queue.append((nb, atom))
        n_mol += 1
    return np.array(atoms, dtype=int), np.array(parent, dtype=int), np.array(mol_id)


def make_whole(
    xyz: np.ndarray, box: np.ndarray, atoms: np.ndarray, parent: np.ndarray
) -> None:
    """
    Make molecules whole in place: every atom is moved to the periodic image
    closest to its parent atom (BFS order, so parents are already whole).
    """
    # depth of each atom in the BFS tree (atoms are in BFS order)
    pos = {a: i for i, a in enumerate(atoms)}
    depth = np.zeros(len(atoms), dtype=int)
    for i, p in enumerate(parent):
        if p >= 0:
            depth[i] = depth[pos[p]] + 1
    inv_box = np.linalg.inv(box)
    for d in range(1, depth.max() + 1 if len(depth) else 1):
        sel = depth == d
        child = atoms[sel]
        par = parent[sel]
        diff = xyz[:, child] - xyz[:, par]
        frac = np.einsum("fni,fij->fnj", diff, inv_box)
        frac -= np.round(frac)
        xyz[:, child] = xyz[:, par] + np.einsum("fni,fij->fnj", frac, box)


def put_com_in_box(
    xyz: np.ndarray,
    box: np.ndarray,
    atoms: np.ndarray,
    mol_id: np.ndarray,
    masses: np.ndarray,
) -> None:
    """Translate each molecule by box vectors so that its COM is inside the box."""
    n_mol = mol_id.max() + 1
    m = masses[atoms].astype(np.float64)
    mol_mass = np.bincount(mol_id, weights=m, minlength=n_mol)
    # molecules without mass (e.g. only virtual sites): use the geometric center
    no_mass = mol_mass <= 0
    if np.any(no_mass):
        m = np.where(no_mass[mol_id], 1.0, m)
        mol_mass = np.bincount(mol_id, weights=m, minlength=n_mol)

    # atoms of a molecule are contiguous (BFS order), so reduceat sums each molecule
    starts = np.flatnonzero(np.r_[True, mol_id[1:] != mol_id[:-1]])
    weighted = xyz[:, atoms].astype(np.float64) * m[None, :, None]
    com = np.add.reduceat(weighted, starts, axis=1) / mol_mass[None, :, None]

    shift_frac = np.floor(_to_frac(com, box))
    shift = _to_cart(shift_frac, box)  # (F, n_mol, 3)
    xyz[:, atoms] -= shift[:, mol_id].astype(xyz.dtype)


def wrap_atoms(xyz: np.ndarray, box: np.ndarray, atoms: np.ndarray) -> None:
    """Put every atom into the box (gromacs -pbc atom)."""
    frac = _to_frac(xyz[:, atoms], box)
    frac -= np.floor(frac)
    xyz[:, atoms] = _to_cart(frac, box)


def treat_pbc(
    trj,
    pbc_level: int,
    center_atom: Optional[int] = None,
    atom_indices: Optional[Iterable[int]] = None,
) -> None:
    """
    Apply the PBC treatment to an mdtraj Trajectory in place.

    trj          : mdtraj.Trajectory
    pbc_level    : 1, 2 or 3
    center_atom  : 0-based atom index centered in the box (pbc_level = 3)
    atom_indices : atoms used in the analysis. Only molecules containing these atoms
                   are made whole / put in the box (for speed). None = all atoms.
                   The centering translation of level 3 is applied to all atoms.
    """
    if pbc_level == 1:
        return
    if trj.unitcell_vectors is None:
        raise ValueError("the trajectory has no box information")

    xyz = trj.xyz  # modified in place
    box = trj.unitcell_vectors.astype(np.float64)

    if pbc_level == 3:
        if center_atom is None:
            raise ValueError("center_atom is required for pbc_level = 3")
        box_center = 0.5 * box.sum(axis=1)  # (F, 3), same as gmx -boxcenter tric
        xyz += (box_center - xyz[:, center_atom]).astype(xyz.dtype)[:, None, :]

    if atom_indices is not None and center_atom is not None:
        atom_indices = list(atom_indices) + [center_atom]
    atoms, parent, mol_id = build_molecules(trj.topology, atom_indices)
    masses = np.array(
        [
            a.element.mass if a.element is not None and a.element.mass else 0.0
            for a in trj.topology.atoms
        ]
    )

    if pbc_level == 3:
        wrap_atoms(xyz, box, atoms)  # -pbc atom
    make_whole(xyz, box, atoms, parent)  # -pbc mol
    put_com_in_box(xyz, box, atoms, mol_id, masses)
