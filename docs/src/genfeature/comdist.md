# comdist
- Center of mass distance
- Calculate the distance between the centers of mass of `s1` and `s2`.

### Example
- The following example generates features about COM distance for MSM analysis

#### mdtraj
```shell
pacs genfeature comdist mdtraj -t 1 -tf prd.xtc -top inputs/example_gromacs/input.gro -s1 "residue 1" -s2 "residue 9" 
```


### Arguments

#### mdtraj
```plaintext
usage: pacs genfeature comdist mdtraj [-h] [-t] [-tf] [-top] [-od] [-p] [-s1] [-s2] 
```

- `-t, --trial` (int):
  - trial number without 0-fill
- `-tf, --trj-file` (str):
  - trajectory file name (e.g. prd.xtc prd_rmmol.trr)
- `-top, --topology` (str):
  - topology file path (e.g. .inputs/input.gro)
- `-od, --outdir` (str):
  - output directory path
- `-p, --n_parallel` (int):
  - number of parallel
- `-s1, --selection1` (str):
  - mdtraj selection1 for calculating distance
- `-s2, --selection1` (str):
  - mdtraj selection2 for calculating distance
