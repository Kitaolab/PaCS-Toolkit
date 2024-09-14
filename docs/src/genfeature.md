# genfeature
- This command should be executed after running `pacs mdrun`.
- It generates feature data in `.npy` format, which is cconvenient for  MSM analysis in Python.
  - Feature data files (e.g., `t001c002r010.npy`) are stored in the directory specified with the `-od` option.
  - Each `.npy` file has the `np.arry` in the shape as described in the table below.
- This command supports parallel processing.


Currently implemented analysis tools and the shape of the output data in `.npy` files.


| feature | mdtraj | gmx | cpptraj | shape of `.npy`        |
| ------- | ------ | --- | ------- | ---------------------- |
| comdist | o      | x   | x       | (n_frames,)            |
| comvec  | o      | x   | x       | (n_frames, 3)          |
| rmsd    | o      | x   | x       | (n_frames,)            |
| xyz     | o      | x   | x       | (n_frames, n_atoms, 3) |
