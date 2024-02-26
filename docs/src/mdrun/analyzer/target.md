# RMSD
- Evaluate snapshots of each trajectory so that the RMSD from the reference structure becomes smaller.
- The structure of the groups specified by `selection1` and `selection3` are superimposed by the least squares method and the RMSD is calculated with the structure of the groups specified by `selection2` and `selection4`.
- Usage Example
  - Finding transitions between two known structures.
- See [here](../inputfile.md#target) for an example input file.  
  
#### keywords
- **type: str, required**
  - evaluation type, "target".
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value falls below this threshold (in units of nm).
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs.
  - If you set `skip_frame=2`, PaCS-MD will use every other frame.
- **analyzer: str, default="mdtraj"**
  - Trajectory tool used to calculate the evaluation value.
  - "mdtraj", "gromacs" and "cpptraj" are supported.
- **reference: str, required**
  - Structure file path for the reference structure of RMSD calculation.
- **selection1: str, required**
  - Selection string or name of index group for specified group in trajectories (least squares fit)
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection2: str, required**
  - Selection string or name of index group for specified group in trajectories (RMSD calculation)
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection3: str, default=`selection1`**
  - Selection string or name of index group for specified group in `reference` (least squares fit)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories.) Otherwise, you don't need to specify this option.
  - This option is valid when `analyzer="mdtraj"` or `analyzer="cpptraj"`.
  - If you use gromacs (`analyzer="gromacs"`), this option is ignored and the same selection indice are automatically used for your trajectories and the `reference`.
- **selection4: str, default=`selection2`**
  - Selection string or name of index group for specified group in `reference` (RMSD calculation)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories.) Otherwise, you don't need to specify this option.
  - This option is valid when `analyzer="mdtraj"` or `analyzer="cpptraj"`.
  - If you use gromacs (`analyzer="gromacs"`), this option is ignored and the same selection indices are automatically used for your trajectories and the `reference`.


#### Papers

~~~
[1] Parallel cascade selection molecular dynamics (PaCS-MD) to generate conformational transition pathway, https://doi.org/10.1063/1.4813023
~~~
