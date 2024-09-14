#!/bin/bash
#PBS -l select=10:ncpus=64:mpiprocs=64:ompthreads=1
#PBS -l walltime=01:00:00

set -e
source /etc/profile.d/modules.sh
module purge
module load gromacs/2022.6

# For conda environment (you need to install pacsmd by yourself)
# module load conda/20230214
# source /lustre/rccs/apl/ap/conda/20230214/etc/profile.d/conda.sh
# conda activate pacs

if [ ! -z "${PBS_O_WORKDIR}"  ]; then
    cd "${PBS_O_WORKDIR}"
fi

export I_MPI_COLL_EXTERNAL=no

for trial in {1..1};
do
    pacs mdrun -f input.toml -t $trial
done

echo "pacsmd done" >&1
