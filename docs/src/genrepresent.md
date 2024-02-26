# genrepresent
- This command is used after executing PaCS-MD.
- This command traces each cycle in reverse order, starting with the frame with the best CV in the last cycle, and generates one continuous trajectory file.
- The generated file is named `repr_complete` and located in the `genrepresent` directory.
- File extension is determined by the user.

### Caution
- This command operates on all of the trajectories in one trial at a time.
- If you want to apply this for the multiplie trials, you could simply write an iteration shell script to achieve it.

### Example
- The following example generates a trajectory file.

#### mdtraj
```shell
pacs genrepresent mdtraj -t 1 -trj prd.xtc -top ./inputs/input.gro
```

#### gromacs
```shell
pacs genrepresent gmx -t 1 -trj prd.xtc -top ./inputs/input.gro -g gmx_mpi
```

#### cpptraj
```shell
pacs genrepresent cpptraj -t 1 -trj prd.nc -top inputs/input.prmtop 
```

### Arguments

#### mdtraj
```plaintext
usage: pacs genrepresent mdtraj [-h] [-t] [-trj] [-top]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-trj, --trajectory` (str): 
    - trajectory file name (e.g. `-trj prd.xtc`)
- `-top, --topology` (str): 
    - topology file path (e.g. `-m trial001/cycle000/replica001/prd.pdb`)

#### gromacs
```plaintext
usage: pacs genrepresent gmx [-h] [-t] [-trj] [-top] [-g]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-trj, --trajectory` (str): 
    - trajectory file name (e.g. `-trj prd.xtc`)
- `-top, --topology` (str): 
    - topology file path (e.g. `-m trial001/cycle000/replica001/input.gro`)
- `-g, --cmd_gmx` (str): 
    - gromacs command prefix (e.g. `-g gmx_mpi`)
  
#### cpptraj
```plaintext
usage: pacs genrepresent cpptraj [-h] [-t] [-trj] [-top]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-trj, --trajectory` (str): 
    - trajectory file name (e.g. `-trj prd.nc`)
- `-top, --topology` (str): 
    - topology file path (e.g. `-m trial001/cycle000/replica001/input.parm7`)

