# A_D
- Evaluate snapshots of each trajectory so that the distance between the centers of mass of the two selected groups fluctuates significantly within a certain range.
- Usage Example
  - Observing large movements of proteins, such as opening and closing.
  - Observing the binding and unbinding of ligands.
- See [here](../inputfile.md#a_d) for an example input file.

#### keywords
- **type: str, required**
  - evaluation type, "a_d".
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
- **d_threshold: float, required**
  - Threshold for switching from dissociation to association mode. If the maximum value of cv calculated while in dissociation mode exceeds this value, it switches to association mode.
- **frame_sel: int, required**
  - One of the conditions used to switch from association to dissociation.
  - If the highest ranking frame in association mode is less than this value, it will be assumed that there has been no change from the previous cycle (i.e., it has come as close as possible).　Hence, we consider the molecule to be within bound.
- **bound_threshold: int, required**
  - One of the conditions used to switch from association to dissociation.
  - When the number of bound cycles exceeds this value, the mode is switched from association to disassociation and the number of bound cycles is initialized to 0.

Papers
~~~
[1] Kinetic Selection and Relaxation of the Intrinsically Disordered Region of
 a Protein upon Binding, https://doi.org/10.1021/acs.jctc.9b01203
~~~
