# comvec
- Center of mass vector

### Example
- The following example generates features about COM vector for MSM analysis

#### mdtraj
```shell
pacs genfeature comvec mdtraj -t 1 -tf prd.xtc -top inputs/input.gro -ref inputs/input.gro -ft "name CA" -fr "name CA" -s1 "resid 1" -s2 "resid 9"
```


### Arguments

#### mdtraj
```plaintext
usage: pacs genfeature comvec mdtraj [-h] [-t] [-tf] [-top] [-od] [-p] [-ref] [-ft] [-fr] [-s1] [-s2]
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
- `-ref, --reference` (str):
  - reference file path for fitting
- `-ft, --fit-trj` (str):
  - fitting selection for mdtraj in trajectory
- `-fr, --fit-ref` (str):
  - fitting selection for mdtraj in reference
- `-s1, --selection1` (str):
  - mdtraj selection1 for calculating distance
- `-s2, --selection1` (str):
  - mdtraj selection2 for calculating distance
