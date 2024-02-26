# rmmol
- This command is used after executing `pacs mdrun`.
- This command removes unnecessary atoms from the trajectory created by running PaCS-MD.
- This command reduces the file size and the burden on the computer capacity.

### Caution
- This command is not reversible.
- This command operates on all trajectories of one trial at a time.
- If you want to apply it to more than one trial, you could easily achieve it by writing an iteration shell script.

### Example
- The following example removes water molecules from the trajectory.

#### mdtraj
```shell
pacs rmmol mdtraj -t 1 -k "not water" -e .xtc -m trial001/cycle000/replica001/prd.gro
```

#### gromacs
```shell
pacs rmmol gmx -t 1 -k "not_water" -e .xtc -n index.ndx -g gmx 
```

#### cpptraj
```shell
pacs rmmol cpptraj -t 1 -k "not water" -e .nc -p trial001/cycle000/replica001/prd.parm7
```


### Arguments

#### mdtraj
```plaintext
usage: pacs rmmol mdtraj [-h] [-t] [-k] [-e] [-m]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-k, --keep_selection` (str): 
    - atom selection to be retained in trajectory (e.g. `-k "not water"`)
- `-e, --trajectory_extension` (str): 
    - trajectory extension (e.g. `-e .xtc`)
- `-m, --top_mdtraj` (str): 
    - topology file path for mdtraj analysis (e.g. `-m trial001/cycle000/replica001/prd.pdb`)

#### gromacs
```plaintext
usage: pacs rmmol gmx [-h] [-t] [-k] [-n] [-g] [-e]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-k, --keep_selection` (str): 
    - index group to be retained in trajectory (e.g. `-k "not_water"`)
- `-e, --trajectory_extension` (str): 
    - gromacs trajectory extension (e.g. `-e .xtc`)
- `-n, --index_file` (str): 
    - index file for gromacs (e.g. `-n index.ndx`)
- `-g, --cmd_gmx` (str): 
    - gromacs command prefix (e.g. `-g gmx`)

  
#### cpptraj
```plaintext
usage: pacs rmmol cpptraj [-h] [-t] [-k] [-e] [-p]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-k, --keep_selection` (str): 
    - atom selection to be retained in trajectory (e.g. `-k :!WAT`)
- `-e, --trajectory_extension` (str): 
    - trajectory extension (e.g. `-e .nc`)
- `-p, --topology` (str): 
    - topology file path for cpptraj analysis (e.g. `-p trial001/cycle000/replica001/prd.parm7`)
