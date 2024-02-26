# Quick Start

- on this page, we will introduce a quick guide on running **dissociation PaCS-MD using gromacs**.
- If you want to try other PaCS-MD, please refer to [Analyzer](reference/analyzer.md).

*Content*
- [Quick Start](#quick-start)
  - [Step1: Installing by pip or conda](#step1-installing-by-pip-or-conda)
  - [Step2: Preparing initial files](#step2-preparing-initial-files)
  - [Step3: Preparing input file for PaCS-MD](#step3-preparing-input-file-for-pacs-md)
  - [Step4: Running PaCS-MD](#step4-running-pacs-md)
    - [Supplement: Runing other trial](#supplement-runing-other-trial)
  - [Step5: Making new fitted trajectories from pacsmd results](#step5-making-new-fitted-trajectories-from-pacsmd-results)
  - [Step6: Extracting collective-variables from fitted trajectories](#step6-extracting-collective-variables-from-fitted-trajectories)
  - [Step7: Building MSM and predicting free energy](#step7-building-msm-and-predicting-free-energy)


## Step1: Installing by pip or conda
1. Running git clone for getting source code
~~~shell
git clone https://github.com/Kitaolab/PaCS-Toolkit.git
~~~

2. Installing with your favorite method
```shell
# Install by pip
pip install -e ".[mdtraj]"

# Or install by conda and pip
conda create -n pacsmd "python>=3.7" -y
conda activate pacsmd
pip install -e ".[mdtraj]"
```
- The above methods are better, but sometimes they are not suitable for a special situation.
- For more information about installation, Please refer to [Install page](install.md).


## Step2: Preparing initial files
- On this page, we will use **gromacs** as simulator.
- In gromacs, **gro, top, mdp and ndx** files are necessary. Please get these files ready.
- Sample jobscripts and input files are [here](https://github.com/Kitaolab/PaCS-Toolkit/tree/main/jobscripts)
<!-- - If you want to run quickly, please use [test dataset](). -->


## Step3: Preparing input file for PaCS-MD
- PaCS-MD requires **a toml format input file.** Please make input.toml
  - Please adjust the above settings as needed.
  - For more information about this file, please refer to [input file](reference/inputfile.md).
```shell
vim input.toml
```
<details><summary> input.toml </summary>

```toml
# Input file for PaCS-MD
## basic
# pacsmd settings
## basic
max_cycle = 2                           # Maximum number of cycles to run. (ex. 1, ..., 123, ..., 999)
n_replica = 3                           # Number of replica. (ex. 1, ..., 123, ..., 999)
n_parallel = 3                          # Number of replica which are calculated at a time
skip_frame = 1                          # Frequency of frames used for ranking among trajectories
centering = true                        # Whether to move the molecule to the center
centering_selection = "protein"         # Name of molecule to move in the center
working_dir = "./."                     # Directory where pacsmd will run

## simulator
simulator = "gromacs"                   # Software used inside PaCS-MD
cmd_mpi = "mpirun -np 4"                # Commands for MPI such as mpirun, blank is OK
cmd_serial = "gmx_mpi mdrun -ntomp 6"   # Commands to run the simulator serially
cmd_parllel = "gmx_mpi mdrun -ntomp 6"  # Commands to run the simulator parallelly
structure = "input.gro"                 # Structural file such as gro, pdb, rst7, etc.
topology = "topol.top"                  # Topology file such as top, parm7, psf, etc.
mdconf = "parameter.mdp"                # Parameter file such as mdp, mdin, namd, etc.
index_file = ".index.ndx"               # Gromacs index file
trajectory_extension = ".xtc"           # Trajectory file extension. ("." is necessary)

## analyzer
type = "dissociation"                   # Evaluation type
threshold = 100                         # CV threshold for determining to terminate a trial
skip_frame = 1                          #  How many frames to skip when ranking CVs
analyzer = "mdtraj"                     # Trajectory tool used to calculate the evaluation type
selection1 = "resid 1 to 5"             # Selection string for specified group in trajectories
selection2 = "resid 6 to 10"            # Selection string for specified group in trajectories

## postprocess
genrepresent = true                     #  Whether genrepresent is executed after trial
rmmol = true                            #  Whether rmmol is executed after each cycle
keep_selection = "not water"            #  Molecular name or index group to be left in the trajectory when rmmol
rmfile = true                           #  Whether rmfile is executed after trial
```

</details>


## Step4: Running PaCS-MD
- Finally, we are ready to perform PaCS-MD
- Specifying the trial id in argument **t** and the input file in argument **f**.
```shell
pacs mdrun -t 1 -f input.toml
```

<details><summary> CAUTION </summary>
In this case, the total core will be 24.

So, 8 cores will be used in each 3 replica at once. (24 / 3 = 8 cores)
</details>


- If you want to continue the simulation from the middle of a cycle or trial, simply run pacsmd again. Completed cycles will be skipped, and the simulation will resume from the the point of interruption.

- You will get the results
~~~shell
$ ls
trial001/
~~~

### Supplement: Runing other trial
- Usually, a single trial is not sufficient for sampling, so multiple trials are required.
- We can run trial2 PaCS-MD
```shell
pacs mdrun -t 2 -f input.toml
```

- Output will be the following
```shell
$ ls
trial002/
```

## Step5: Making new fitted trajectories from pacsmd results
- Before performing visual_pathway or MSM(especially 3D-MSM and volume correction and etc.) and etc, you need to make fitted trajectories from pacsmd results
- For fitting, we prepare `pacsmd fitting mdtraj` command. But you can use existing software such as `gmx trjconv` or `cpptraj` as usual.
- See [function](./reference_manual/function.md) for more information.
```shell
$ pacs fit mdtraj -s rmmol_top.pdb -r ref.gro -ts protein -rs protein -tf prd_rmmol.xtc -t 1 -p 1
```

## Step6: Extracting collective-variables from fitted trajectories
- After making fitted trajectories, you need to extract CV to build MSM, where CV denotes collective variables such as "distance" and "inter COM vector" and "PCA" and etc.
- For extracting CVs, we got `pacsmd cv` command. But this command provides you only frequently used CV such as comd-distance, com-vector, pca, tica and rmsd.
- So if you want to use other specific CVs, you need to write a code by yourself.

~~~shell
$ pacs genfeature mdtraj comdist -s input.gro -s1 "resname Lig" -s2 "protein" -tf prd.xtc -t 1 -p 1
$ ls
comdist-CV/
~~~


## Step7: Building MSM and predicting free energy
- After extracting CVs, you would like to obtain free energy landscape related to extracted CVs.
- To calculate free energy, we provide MSM notebooks. The notebooks outline the process for computing free energy landscape.
- But these are just sample notebooks, so you need to check carefully when you use these notebook.
~~~shell
$ code pacsmd/MSM/distance.ipynb
~~~

