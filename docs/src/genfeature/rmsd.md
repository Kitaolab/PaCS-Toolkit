# RMSD
- Root Mean Square Deviation

### Example
- The following example generates features about RMSD for MSM analysis

#### mdtraj
```shell
pacs genfeature rmsd mdtraj -t 1 -tf prd.xtc -top ./inputs/input.gro -ref ./inputs/input.gro -ft "protein" -fr "protein" -ct "name CA" -cr "name CA"
```


### Arguments

#### mdtraj
```plaintext
usage: pacs genfeature pca mdtraj [-h] [-tf] [-top] [-od] [-p] [-ref] [-ft] [-fr] [-ct] [-cr]
```

- `-t, --trial` (int):
  - trial number without 0-fill
- `-tf, --trj-file` (str):
  - trajectory file name (ex. prd.xtc prd_rmmol.trr)
- `-top, --topology` (str):
  - topology file path (ex. .inputs/input.gro)
- `-od, --outdir` (str):
  - output directory path
- `-p, --n_parallel` (int):
  - number of parallel
- `-ref, --reference` (str):
  - reference file path for fitting/RMSD calculation
- `-ft, --fit-trj` (str):
  - mdtraj selection for fitting in trajectory
- `-fr, --fit-ref` (str):
  - mdtraj selection for fitting in reference
- `-ct, --cal-trj` (str):
  - mdtraj selection for calculating RMSD in trajectory
- `-cr, --cal-ref` (str):
  - mdtraj selection for calculating RMSD in reference
