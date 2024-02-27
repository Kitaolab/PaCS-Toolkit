# Input file

- PaCS-MD requires an input file. Here are the variables in the input file
- input file must be in [toml format](https://toml.io/en/).

*Contents*
- [sample input file](#sample-input-file)
- [basic option](#basic-option)
- [simulator option](#simulator-option)
  - [Gromacs](#gromacs)
  - [Amber](#amber)
  - [NAMD](#namd)
- [analyzer option](#analyzer-option)
  - [Target](#target)
  - [RMSD](#rmsd)
  - [Association](#association)
  - [Dissociation](#dissociation)
  - [EdgeExpansion](#edgeexpansion)
  - [A\_D](#a_d)
  - [Template](#template)
- [hidden option (No need to specify)](#hidden-option-no-need-to-specify)

## sample input file
- please check [here](https://github.com/Kitaolab/PaCS-Toolkit/tree/main/jobscripts)


## basic option
<details><summary> click here </summary>

- **max_cycle: int, default=1**
  - Maximum number of cycles to run. (ex. 1, ..., 123, ..., 999)
- **n_replica: int, default=1**
  - Number of replica. (ex. 1, ..., 123, ..., 999)
- **n_parallel: int, default=1**
  - Number of replica calculated at a time
- **centering: bool, default=True**
  - Whether to bring the molecule selected by centering_selection to the center of the simulation cell when creating the initial structure for the next cycle
- **centering_selection: str, default="protein" or "Protein" or "@CA,C,O,N,H"**
  - Molecules to be moved to the center
  - default value will be changed to match `analyzer`
    - if `analyzer` == "mdtraj", default="protein"
    - if `analyzer` == "gromacs", default="Protein"
    - if `analyzer` == "cpptraj", default="@CA,C,O,N,H"
- **working_dir: str, default="./."**
  - Directory where pacsmd will run
- **rmmol: bool, default=false**
  - Whether rmmol is executed after each cycle
- **keep_selection: str, (required if `rmmol=true`)**
  - Molecular name or index group to be left in the trajectory when rmmol
- **rmfile: bool, default=false**
  - Whether rmfile is executed after trial
</details>


```toml
max_cycle = 2                     # Maximum number of cycles to run. (ex. 1, ..., 123, ..., 999)
n_replica = 3                     # Number of replica. (ex. 1, ..., 123, ..., 999)
n_parallel = 3                    # Number of replica calculated at a time
centering = true                  # Whether to move the molecule to the center
centering_selection = "protein"   # Name of molecule to move in the center
working_dir = "/work/"            # Directory where pacsmd will run
rmmol = true                      # Whether rmmol is executed after each cycle
keep_selection = "not water"      # Molecular name or index group to be kept in the trajectory when rmmol
rmfile = true                     # Whether rmfile is executed after trial
```


## simulator option

| analyzer \ simulator | gromacs | amber | namd |
| -------------------- | ------- | ----- | ---- |
| mdtraj               | o       | o     | o    |
| gromacs              | o       | x     | x    |
| cpptraj              | x       | o     | x    |

### Gromacs
<details><summary> click here </summary>

- **simulator: str, required**
  - Software used inside PaCS-MD
- **cmd_mpi: str, default=""**
  - Commands for MPI such as mpirun, blank is OK
- **cmd_serial: str, required**
  - Commands to run the simulator serially
- **cmd_parallel: str, default=cmd_serial**
  - Commands to run the simulator parallelly
- **structure: str, required**
  - Structural file such as gro, pdb, rst7, etc.
- **topology: str, required**
  - Topology file such as top, parm7, psf, etc.
- **mdconf: str, required**
  - Parameter file such as mdp, mdin, namd, etc.
- **index_file: str, (required if Gromacs)**
  - Gromacs index file
- **trajectory_extension: str, required**
  - Trajectory file extension. ("." is necessary)

</details>

```toml
simulator = "gromacs"                   # Software used inside PaCS-MD
cmd_mpi = "mpirun -np 4"                # Commands for MPI such as mpirun, blank is OK
cmd_serial = "gmx_mpi mdrun -ntomp 6"   # Commands to run the simulator serially
cmd_parllel = "gmx_mpi mdrun -ntomp 6"  # Commands to run the simulator parallelly
structure = "/work/input.gro"           # Structural file such as gro, pdb, rst7, etc.
topology = "/work/topol.top"            # Topology file such as top, parm7, psf, etc.
mdconf = "/work/parameter.mdp"          # Parameter file such as mdp, mdin, namd, etc.
index_file = "/work/index.ndx"          # Gromacs index file
trajectory_extension = ".xtc"           # Trajectory file extension. ("." is necessary)
```


### Amber
<details><summary> click here </summary>

- **simulator: str, required**
  - Software used inside PaCS-MD
- **cmd_mpi: str, default=""**
  - Commands for MPI such as mpirun, blank is OK
- **cmd_serial: str, required**
  - Commands to run the simulator serially
- **cmd_parallel: str, default=cmd_serial**
  - Commands to run the simulator parallelly
- **structure: str, required**
  - Structural file such as gro, pdb, rst7, etc.
- **topology: str, required**
  - Topology file such as top, parm7, psf, etc.
- **mdconf: str, required**
  - Parameter file such as mdp, mdin, namd, etc.
- **trajectory_extension: str, required**
  - Trajectory file extension. ("." is necessary)

</details>

```toml
simulator = "amber"                     # Software used inside PaCS-MD
cmd_mpi = ""                            # Commands for MPI such as mpirun, blank is OK
cmd_serial = "pmemd.cuda"               # Commands to run the simulator serially
cmd_parllel = "pmemd.cuda"              # Commands to run the simulator parallelly
structure = "/work/structure.rst7"      # Structural file such as gro, pdb, rst7, etc.
topology = "/work/topology.parm7"       # Topology file such as top, parm7, psf, etc.
mdconf = "/work/parameter.mdin"         # Parameter file such as mdp, mdin, namd, etc.
trajectory_extension = ".nc"            # Trajectory file extension. ("." is necessary)
```



### NAMD
<details><summary> click here </summary>

- **simulator: str, required**
  - Software used inside PaCS-MD
- **cmd_mpi: str, default=""**
  - Commands for MPI such as mpirun, blank is OK
- **cmd_serial: str, required**
  - Commands to run the simulator serially
- **cmd_parallel: str, default=cmd_serial**
  - Commands to run the simulator parallelly
- **structure: str, required**
  - Structural file such as gro, pdb, rst7, etc.
- **topology: str, required**
  - Topology file such as top, parm7, psf, etc.
- **mdconf: str, required**
  - Parameter file such as mdp, mdin, namd, etc.
- **trajectory_extension: str, required**
  - Trajectory file extension. ("." is necessary)

</details>

```toml
simulator = "namd"                      # Software used inside PaCS-MD
cmd_mpi = "mpirun -np 4"                # Commands for MPI such as mpirun, blank is OK
cmd_serial = "namd2 +p6"                # Commands to run the simulator serially
cmd_parllel = "namd2 +p6"               # Commands to run the simulator parallelly
structure = "/work/input.pdb"           # Structural file such as gro, pdb, rst7, etc.
topology = "/work/ionized.psf"          # Topology file such as top, parm7, psf, etc.
mdconf = "/work/production.namd"        # Parameter file such as mdp, mdin, namd, etc.
trajectory_extension = ".dcd"           # Trajectory file extension. ("." is necessary)
```


## analyzer option

| analyzer \ type | dissociation | association | rmsd | target | ee  | a_d | template |
| --------------- | ------------ | ----------- | ---- | ------ | --- | --- | -------- |
| mdtraj          | o            | o           | o    | o      | o   | o   | -        |
| gromacs         | o            | o           | o    | o      | x   | o   | -        |
| cpptraj         | o            | o           | o    | o      | x   | o   | -        |


### Target
<details><summary> click here </summary>

- **type: str, required**
  - evaluation type, "target".
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value falls below this threshold (in units of nm).
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs.
  - If you set `skip_frame=2`, PaCS-MD will use every other frame.
- **analyzer: str, default="mdtraj"**
  - Trajectory tool used to calculate the evaluation value.
  - "mdtraj", "gromacs" and "cpptraj" are supported.
- **reference: str, required**
  - Structure file path for the reference structure of RMSD calculation.
- **selection1: str, required**
  - Selection string or name of index group for specified group in trajectories (least squares fit)
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection2: str, required**
  - Selection string or name of index group for specified group in trajectories (RMSD calculation)
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection3: str, default=`selection1`**
  - Selection string or name of index group for specified group in `reference` (least squares fit)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories.) Otherwise, you don't need to specify this option.
  - This option is valid when `analyzer="mdtraj"` or `analyzer="cpptraj"`.
  - If you use gromacs (`analyzer="gromacs"`), this option is ignored and the same selection indices are automatically used for your trajectories and the `reference`.
- **selection4: str, default=`selection2`**
  - Selection string or name of index group for specified group in `reference` (RMSD calculation)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories.) Otherwise, you don't need to specify this option.
  - This option is valid when `analyzer="mdtraj"` or `analyzer="cpptraj"`.
  - If you use gromacs (`analyzer="gromacs"`), this option is ignored and the same selection indices are automatically used for your trajectories and the `reference`.


</details>

```toml
type = "target"                 # Evaluation type
threshold = 0.01                # CV threshold used to decide whether to terminate the calculation (in units of nm)
skip_frame = 1                  # How many frames to skip when ranking CVs

# if analyzer == "mdtraj"
analyzer = "mdtraj"             # Trajectory tool used to calculate the evaluation type
reference = "/work/ref.pdb"     # Structure for comparison
selection1 = "backbone"         # Selection string for specified group in trajectroies (least squares fit)
selection2 = "backbone"         # Selection string for specified group in trajectories (RMSD calculation)
selection3 = "backbone and (not resid 1 to 10)"         # Selection string for specified group in reference (least squares fit)
selection4 = "backbone and (not resid 1 to 10)"         # Selection string for specified group in reference (RMSD calculation)

# else if analyzer == "gromacs"
# analyzer = "gromacs"          # Trajectory tool used to calculate the evaluation type
# selection1 = "Backbone"       # Name of index group for specified group in trajectories (least squares fit)
# selection2 = "Backbone"       # Name of index group for specified group in trajectories (RMSD calculation)

# else if analyzer == "cpptraj"
# analyzer = "cpptraj"          # Trajectory tool used to calculate the evaluation type
# selection1 = "@CA,N,O,C"      # Selection string for specified group in trajectroies (least squares fit)
# selection2 = "@CA,N,O,C"      # Selection string for specified group in trajectories (RMSD calculation)
```


### RMSD
<details><summary> click here </summary>

- **type: str, required**
  - evaluation type, "rmsd"
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value exceeds this threshold (in units of nm).
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs.
  - If you set `skip_frame=2`, PaCS-MD will use every other frame.
- **analyzer: str, default="mdtraj"**
  - Trajectory tool used to calculate the evaluation value.
  - "mdtraj", "gromacs" and "cpptraj" are supported.
- **reference: str, required**
  - Structure file path for the reference structure of RMSD calculation.
- **selection1: str, required**
  - Selection string or name of index group for specified group in trajectories (least squares fit)
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection2: str, required**
  - Selection string or name of index group for specified group in trajectories (RMSD calculation)
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs supported only)
- **selection3: str, default=`selection1`**
  - Selection string or name of index group for specified group in `reference` (least squares fit)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories.) Otherwise, you don't need to specify this option.
  - This option is valid when `analyzer="mdtraj"` or `analyzer="cpptraj"`.
  - If you use gromacs (`analyzer="gromacs"`), this option is ignored and the same selection indices are automatically used for your trajectories and the `reference`.
- **selection4: str, default=`selection2`**
  - Selection string or name of index group for specified group in `reference` (RMSD calculation)
  - If your `reference` structure has different topology from your trajectories, you can utilize this option. (e.g. `reference` has different configuration about mutation, missing residues or modified residues from your the trajectories.) Otherwise, you don't need to specify this option.
  - This option is valid when `analyzer="mdtraj"` or `analyzer="cpptraj"`.
  - If you use gromacs (`analyzer="gromacs"`), this option is ignored and the same selection indices are automatically used for your trajectories and the `reference`.

</details>

```toml
type = "rmsd"                   # Evaluation type
threshold = 2                   # CV threshold used to decide whether to terminate the calculation (in units of nm)
skip_frame = 1                  # How many frames to skip when ranking CVs

# if analyzer == "mdtraj"
analyzer = "mdtraj"             # Trajectory tool used to calculate the evaluation type
reference = "/work/ref.pdb"     # Structure for comparison
selection1 = "backbone"         # Selection string for specified group in trajectories (least squares fit)
selection2 = "backbone"         # Selection string for specified group in trajectories (RMSD calculation)
selection3 = "backbone and (not resid 1 to 10)"         # Selection string for specified group in reference (least squares fit)
selection4 = "backbone and (not resid 1 to 10)"         # Selection string for specified group in reference (RMSD calculation)

# else if analyzer == "gromacs"
# analyzer = "gromacs"          # Trajectory tool used to calculate the evaluation type
# selection1 = "Backbone"       # Name of index group for specified group in trajectories (least squares fit)
# selection2 = "Backbone"       # Name of index group for specified group in trajectories (RMSD calculation)

# else if analyzer == "cpptraj"
# analyzer = "gromacs"          # Trajectory tool used to calculate the evaluation type
# selection1 = "@CA,N,O,C"      # Selection string for specified group in trajectories (least squares fit)
# selection2 = "@CA,N,O,C"      # Selection string for specified group in trajectories (RMSD calculation)
```


### Association
<details><summary> click here </summary>

- **type: str, required**
  - evaluation type, "association".
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value falls below this threshold (in units of nm).
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

</details>

```toml
type = "association"            # Evaluation type
threshold = 0.3                 # CV threshold used to decide whether to terminate the calculation (in units of nm)
skip_frame = 1                  # How many frames to skip when ranking CVs

# if analyzer == "mdtraj"
analyzer = "mdtraj"             # Trajectory tool used to calculate the evaluation type
selection1 = "resid 1 to 5"     # Selection string for specified group in trajectories
selection2 = "resid 6 to 10"    # Selection string for specified group in trajectories

# else if analyzer == "gromacs"
# analyzer = "gromacs"          # Trajectory tool used to calculate the evaluation type
# selection1 = "resid_1_to_5"   # Name of index group for specified group in trajectories
# selection2 = "resid_6_to_10"  # Name of index group for specified group in trajectories

# else if analyzer == "cpptraj"
# analyzer = "cpptraj"          # Trajectory tool used to calculate the evaluation type
# selection1 = ":1-5"           # Name of index group for specified group in trajectories
# selection2 = ":6-10"          # Name of index group for specified group in trajectories
```


### Dissociation
<details><summary> click here </summary>

- **type: str, required**
  - evaluation type, "dissociation".
- **threshold: float, required**
  - PaCS-MD terminates the calculation when the evaluation value exceeds this threshold.
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs
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

</details>

```toml
type = "dissociation"           # Evaluation type
threshold = 10                  # CV threshold used to decide whether to terminate the calculation (in units of nm)
skip_frame = 1                  # How many frames to skip when ranking CVs

# if analyzer == "mdtraj"
analyzer = "mdtraj"             # Trajectory tool used to calculate the evaluation type
selection1 = "resid 1 to 5"     # Selection string for specified group in trajectories
selection2 = "resid 6 to 10"    # Selection string for specified group in trajectories

# else if analyzer == "gromacs"
# analyzer = "gromacs"      # Trajectory tool used to calculate the evaluation type
# selection1 = "resid_1_to_5"   # Name of index group for specified group in trajectories
# selection2 = "resid_6_to_10"  # Name of index group for specified group in trajectories

# else if analyzer == "cpptraj"
# analyzer = "cpptraj"          # Trajectory tool used to calculate the evaluation type
# selection1 = ":1-5"           # Name of index group for specified group in trajectories
# selection2 = ":6-10"          # Name of index group for specified group in trajectories
```


### EdgeExpansion
<details><summary> click here </summary>

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

</details>

```toml
type = "ee"                     # Evaluation type
skip_frame = 1                  # How many frames to skip when ranking CVs

# if analyzer == "mdtraj"
analyzer = "mdtraj"             # Trajectory tool used to calculate the evaluation type
selection1 = "backbone"         # Selection string for specified group in trajectories (least squares fit)
selection2 = "backbone"         # Selection string for specified group in trajectories (RMSD calculation)
selection3 = "backbone"         # Selection string for specified group in reference (least squares fit)
selection4 = "backbone"         # Selection string for specified group in reference (RMSD calculation)
```


### A_D
<details><summary> click here </summary>

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
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs is only supported)
- **selection2: str, required**
  - Selection string or name of index group for specified group in trajectories
  - Depending on the `analyzer`, there are different ways to specify `selection`.
    - If you use mdtraj (`analyzer="mdtraj"`), the `selection` should follow mdtraj's atom selection. e.g. "resid 5 to 100 and name CA"
    - If you use gromacs (`analyzer="gromacs"`), the `selection` should follow Gromacs index group in `index.ndx`. (Gromacs is only supported)
- **d_threshold: float, required**
  - Threshold for switching from dissociation to association mode. If the maximum value of cv calculated while in dissociation mode exceeds this value, it switches to associtaion mode.
- **frame_sel: int, required**
  - One of the conditions used to switch from association to dissociation.
  - If the highest ranking frame in association mode is less than this value, it is judged that there has been no change from the previous cycle (i.e., it has come as close as it can).　Also, at this time, we consider it to be within bound.
- **bound_threshold: int, required**
  - One of the conditions used to switch from association to dissociation.
  - When the number of bound cycles exceeds this value, the mode is switched from association to disassociation and the number of bound cycles is initialized to 0. When the number of bound cycles exceeds this value, the mode is switched from association to disassociation and the number of bound cycles is initialized to 0.

</details>

```toml
type = "a_d"                    # Evaluation type
skip_frame = 1                  # How many frames to skip when ranking CVs

# if analyzer == "mdtraj"
analyzer = "mdtraj"             # Trajectory tool used to calculate the evaluation type
selection1 = "resid 1"          # Selection string for specified group in trajectories
selection2 = "resid 9"          # Selection string for specified group in trajectories
d_threshold = 3.0               # threshold for dissociation to association
frame_sel = 5                   # number of frames to be used for judging whether the system has converged
bound_threshold = 3             # threshold for association to dissociation
```


### Template
<details><summary> click here </summary>

- **type: str, required**
  - Evaluation type
- **skip_frame: int, default=1**
  - Number of frames to skip when ranking CVs
- **threshold: float, required**
  - CV threshold for determining to terminate a trial
> Template type is a type that can be defined by the user. It is possible to include user-specific variables in input.toml, and these variables can be used in template type in which they are defined. For more information, click [here](./analyzer/template.md).

</details>

~~~toml
type = "template"
threshold = "???"

# user defined variable
user-defined-variable1 = 123
user-defined-variable2 = "hoge"
...
~~~

## hidden option (No need to specify)
<details><summary> click here </summary>
- **cmd_gmx: str**
  - Gromacs command (ex. gmx, gmx_mpi)
  - will be created from `cmd_serial`
- **top_mdtraj: str**
  - topology file for mdtraj
  - will be created from `input.toml`
- **structure_extension: str**
  - Structure file extension
  - will be created from `structure`
</details>
