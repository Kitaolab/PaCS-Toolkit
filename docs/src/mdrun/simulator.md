# Simulator

- In PaCS-MD, simulations corresponding to the `simulator` are executed. Gromacs, Amber, and NAMD are supported.
- In each cycle, `n_replica` simulations are executed. `n_parallel` simulations are will run in parallel. If `n_replica` is not a multiple of `n_parallel`, or in cycle 0, the remainder of the simulations will run in series.
- If you want to run multiple replica simulations in parallel using MPI, set `cmd_mpi`. If `cmd_mpi` is not set, parallel execution will be performed using the multiprocessing module of python.

*Content*
- [When are `cmd_serial` \& `cmd_parallel` used ?](#when-are-cmd_serial--cmd_parallel-used-)
- [Gromacs](#gromacs)
    - [keywords](#keywords)
- [Amber](#amber)
    - [keywords](#keywords-1)
- [NAMD](#namd)
    - [keywords](#keywords-2)


## When are `cmd_serial` & `cmd_parallel` used ?
- See the table below for `cmd_serial` and `cmd_parallel` in the input file. `cmd_serial` is used if cycle0 or `n_parallel`=1. If `n_replica` is not divisible by `n_parallel`, then `cmd_serial` is used for the remaining replicas. Otherwise, `cmd_parallel` is used.

| GPU | MPI | n_parallel | command      |
| --- | --- | ---------- | ------------ |
| x   | x   | 1          | cmd_serial   |
| x   | x   | n          | cmd_serial   |
| x   | o   | 1          | cmd_serial   |
| x   | o   | n          | cmd_parallel |
| o   | x   | 1          | cmd_serial   |
| o   | x   | n          | cmd_serial   |
| o   | o   | 1          | cmd_seiral   |
| o   | o   | n          | cmd_parallel |

## Gromacs
To run the simulation using gromacs, write in the inputfile as in [this example](inputfile.md#gromacs). The details of each keyword are as follows.

#### keywords
- **simulator: str, required**
  - Software used inside PaCS-MD. e.g. "gromacs"
- **cmd_mpi: str, default=""**
  - Command for MPI parallelizataion. e.g. "mpirun -np 4"
- **cmd_serial: str, required**
  - Command to run simulation in serial. e.g. "gmx_mpi mdrun -ntomp 6"
- **cmd_parallel: str, default=cmd_serial**
  - Command to run simulation in parallel. e.g. "gmx_mpi mdrun -ntomp 6"
- **structure: str, required**
  - Structure file path for MD simulation. e.g. "./input.gro"
  - This is also used as the initial structure of PaCS-MD
- **topology: str, required**
  - Topology file path for MD simulation. e.g. "./topol.top"
- **mdconf: str, required**
  - Parameter file path for MD simulation. e.g. "./parameter.mdp"
- **index_file: str, required**
  - Gromacs index file path. e.g. "./index.ndx"
- **trajectory_extension: str, required**
  - Trajectory file extension. (The "." is necessary.) e.g. ".trr"

## Amber
To run the simulation using amber, write in the inputfile as in [this example](inputfile.md#amber). The details of each keyword are as follows.

#### keywords
- **simulator: str, required**
  - Software used inside PaCS-MD. e.g. "amber"
- **cmd_mpi: str, default=""**
  - Command for MPI such as mpirun. e.g. "mpirun -np 4"
- **cmd_serial: str, required**
  - Command to run simulation in serial. e.g. "pmemd.cuda"
- **cmd_parallel: str, default=cmd_serial**
  - Command to run simulation in parallel. e.g. "pmemd.cuda"
- **structure: str, required**
  - Structure file path for MD simulation. e.g. "./input.rst7"
  - This is also used as the initial structure of PaCS-MD.
- **topology: str, required**
  - Topology file path for MD simulation. e.g. "./topology.parm7"
- **mdconf: str, required**
  - Parameter file path for MD simulation. e.g. "./parameter.mdin"
- **trajectory_extension: str, required**
  - Trajectory file extension. (The "." is necessary.) e.g. ".nc"

## NAMD
To run the simulation using NAMD, write in the inputfile as in [this example](inputfile.md#namd). The details of each keyword are as follows.

#### keywords
- **simulator: str, required**
  - Software used inside PaCS-MD. e.g. "namd"
- **cmd_mpi: str, default=""**
  - Command for MPI parallelizataion. e.g. "mpirun -np 4"
- **cmd_serial: str, required**
  - Command to run simulation in serial. e.g. "namd2 +p4"
- **cmd_parallel: str, default=cmd_serial**
  - Command to run simulation in parallel. e.g. "namd2 +p4"
- **structure: str, required**
  - Structure file path for MD simulation. e.g. "./input.pdb"
  - This is also used as the initial structure of PaCS-MD.
- **topology: str, required**
  - Topology file path for MD simulation. e.g. "./topology.psf"
- **mdconf: str, required**
  - Parameter file path for MD simulation. e.g. "./parameter.conf"
- **trajectory_extension: str, required**
  - Trajectory file extension. (The "." is necessary.) e.g. ".dcd"



