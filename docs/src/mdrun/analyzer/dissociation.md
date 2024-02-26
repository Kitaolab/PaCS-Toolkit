# Dissociation
- Evaluate snapshots of each trajectory so that the centers of mass of the two selected groups are far apart.
- The two selected groups are `selection1` and `selection2` in the input file.  
  
- Usage Example
  - Ligand dissociating from a protein
  - Separate the distance between the two domains of a protein

- See [here](../inputfile.md#dissociation) for an example input file.

#### keywords
- **type: str, required**
  - evaluation type, "dissociation".
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value exceeds this threshold.
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs
  - If you set `skip_frame=2`, PaCS-MD will use every other frame.
- **analyzer: str, default="mdtraj"**
  - Trajectory tool used to calculate the evaluation value.
  - "mdtraj", "gromacs" and "cpptraj" are supported.
- **selection1: str, required**
  - Selection string or name of index group for specified group in trajectories
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection2: str, required**
  - Selection string or name of index group for specified group in trajectories
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)


#### Papers 

```
[1] Protein-Ligand Dissociation Simulated by Parallel Cascade Selection Molecular Dynamics, https://doi.org/10.1021/acs.jctc.7b00504
[2] Dissociation Process of a MDM2/p53 Complex Investigated by Parallel Cascade Selection Molecular Dynamics and the Markov State Model, https://doi.org/10.1021/acs.jpcb.8b10309
[3] Binding free energy of protein/ligand complexes calculated using dissociat
ion Parallel Cascade Selection Molecular Dynamics and Markov state model, http
s://doi.org/10.2142/biophysico.bppb-v18.037
[4] High pressure inhibits signaling protein binding to the flagellar motor an
d bacterial chemotaxis through enhanced hydration, https://doi.org/10.1038/s41
598-020-59172-3
[5] Dissociation Pathways of the p53 DNA Binding Domain from DNA and Critical
Roles of Key Residues Elucidated by dPaCS-MD/MSM, https://doi.org/10.1021/acs.
jcim.1c01508
```
