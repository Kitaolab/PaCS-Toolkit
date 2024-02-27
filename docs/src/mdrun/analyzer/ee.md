# EdgeExpansion
- Evaluate snapshots of each trajectory so that the frame forms the convex hull of the 4-dimentional principal component space(PCs).
- Snapshots of each cycle are projected onto a 4-dimensional principal component spaces (PCs). Its convex hull is computed and the initial structure of the next cycle is selected from the polygon's vertices.
- Usage Example
  - Sampling a wide range of phase space without knowing the reference structure
- See [here](../inputfile.md#edgeexpansion) for an example input file.

#### keywords
- **type: str, required**
  - Evaluation type, "ee".
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs.
  - If you set `skip_frame=2`, PaCS-MD will use every other frame.
- **analyzer: str, default="mdtraj"**
  - Trajectory tool used to calculate the evaluation value.
  - only "mdtraj" is supported.
- **reference: str, required**
  - Trajectory file used to compute the covariance matrix in Principal Component Analysis (PCA).
  - If this value is not set, the covariance matrix is computed based on the trajectory of cycle 0.
- **selection1: str, required**
  - Selection string or name of index group for specified group in trajectories (least squares fit)
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection.
- **selection2: str, required**
  - Selection string or name of index group for specified group in trajectories (PCA calculation)
  - No correction by atomic weights or number of atoms is made when calculating the covariance matrix or projecting.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection.
- **selection3: str, default=`selection1`**
  - Selection string or name of index group for specified group in `reference` (least squares fit)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories)
  - Otherwise, you don't need to specify this option.
- **selection4: str, default=`selection2`**
  - Selection string or name of index group for specified group in `reference`  (PCA calculation)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories)
  - Otherwise, you don't need to specify this option.

#### Papers

~~~
[1] Edge expansion parallel cascade selection molecular dynamics simulation for investigating large-amplitude collective motions of proteins, https://doi.org/10.1063/5.0004654
~~~
