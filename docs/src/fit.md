# fit
- This command is used after executing `pacs mdrun`
- This command makes new trajectories that fit to the reference structure.
- The newly created trajectories are placed in the same hierarchy as the original trajectories.

### Caution
- Fitting the molecules by using the script could take a long time (around 1 hour
for 1 trial)

### Example
- In the following example, trajectories for all cycles and all replicas of trial1 are fitted with the protein, and then the output files are saved.

#### for single trajectory
```shell
pacs fit traj mdtraj -tf ./trial001/cycle001/replica001/prd.xtc -top ./inputs/input.gro -r ./inputs/input.gro -ts "backbone" -rs "backbone"
```

#### for single trial
```shell
pacs fit trial mdtraj -t 1 -s ./trial001/cycle001/replica001/prd.pdb -r ./trial001/cycle001/replica001/prd.pdb -ts "protein" -rs "protein" -tf prd.xtc -p 10
```

### Arguments

#### for single trajectory
```plaintext
usage: pacs fit mdtraj [-h] [-tf] [-top] [-r] [-ts] [-rs] [-p] [-o]
```
- `-tf, --trj_file` (str): 
    - file name of the trajectory to be fitted (e.g. `-tf prd.xtc`)
- `-top, --topology` (str): 
    - topology file path for loading trajectory (e.g. `-s trial001/cycle000/replica001/prd.pdb`)
- `-r, --ref_structure` (str): 
    - reference structure file path for fitting reference (e.g. `-r trial001/cycle000/replica001/prd.pdb`)
- `-ts, --trj_selection` (str): 
    - atom selection for fitting trajectory (e.g. `-ts "protein"`)
- `-rs, --ref_selection` (str): 
    - atom selection for fitting reference (e.g. `-rs "protein"`)
- `-p, --parallel` (int): 
    - number of parallel processes (e.g. `-p 10`)
    - default: 1
- `-o, --out` (str): 
    - output file name (e.g. `-o prd_fit.xtc`)
    - default: `{trj_file}_fit.{ext}`
  
#### for single trial
```plaintext
usage: pacs fit trial mdtraj [-h] [-t] [-tf] [-top] [-r] [-ts] [-rs] [-p] [-o]
```

- `-t, --trial` (int): 
    - trial number (e.g. `-t 1`)
- `-tf, --trj_file` (str): 
    - file name of the trajectory to be fitted (e.g. `-tf prd.xtc`)
- `-top, --topology` (str): 
    - topology file path for loading trajectory (e.g. `-s trial001/cycle000/replica001/prd.pdb`)
- `-r, --ref_structure` (str): 
    - reference structure file path for fitting reference (e.g. `-r trial001/cycle000/replica001/prd.pdb`)
- `-ts, --trj_selection` (str): 
    - atom selection for fitting trajectory (e.g. `-ts "protein"`)
- `-rs, --ref_selection` (str): 
    - atom selection for fitting reference (e.g. `-rs "protein"`)
- `-p, --parallel` (int): 
    - number of parallel processes (e.g. `-p 10`)
    - default: 1
- `-o, --out` (str): 
    - output file name (e.g. `-o prd_fit.xtc`)
    - default: `{trj_file}_fit.{ext}`