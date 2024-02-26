# XYZ
- (x, y, z), 3 dimension coordinates

### Example
- The following example generates features about (x, y, z) for MSM analysis

#### mdtraj
```shell
pacs genfeature xyz mdtraj -t 1 -tf prd.xtc -top ./trial001/cycle000/replica001/input.gro -s "residue 1 to 5"
```


### Arguments

#### mdtraj
```plaintext
usage: pacs genfeature xyz mdtraj [-h] [-t] [-tf] [-top] [-od OUTDIR] [-p N_PARALLEL] [-s] 
```

- `-t, --trial` (int):
  - trial number without 0-fill
- `-tf, --trj-file` (str):
  - trajectory file name (ex. prd.xtc prd_rmmol.trr)
- `top, --topology` (str):
  - topology file path (ex. .inputs/input.gro)
- `-od, --outdir` (str):
  - output directory path
- `-p, --n_parallel` (int):
  - number of parallel
- `-s, --selection` (str):
  - mdtraj selection extracted in trajectory
