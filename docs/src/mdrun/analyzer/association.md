# Association
- Evaluate snapshots of each trajectory so that the centers of mass of the two selected groups are close together.
- The two selected groups are `selection1` and `selection2` in the input file.
  
- Usage Example
  - Bringing a ligand closer to a protein
  - Bringing two domains of a protein closer together  
  
- See [here](../inputfile.md#association) for an example input file.

#### keywords
- **type: str, required**
  - evaluation type, "association".
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value falls below this threshold (in units of nm).
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs.
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
