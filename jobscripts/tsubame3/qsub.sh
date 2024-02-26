#!/bin/bash
#$ -cwd
#$ -l q_node=10
#$ -l h_rt=-01:00:00
#$ -N q_node

set -e
. /etc/profile.d/modules.sh
module purge
module load cuda/11.5.0
module load intel-mpi/21.2.0
module load python/3.9.2
module load gromacs/2022

# Please activate the python environment in which you can use pacsmd library
# Change the path to your environment
# source /home/3/xxBxxxxx/tools/anaconda3/etc/profile.d/conda.sh
# conda activate pacs

for trial in {1..1};
do
    pacs mdrun -f input.toml -t $trial
done

echo "pacsmd done" >&1

# Simulation speed measured by this script and the corresponding .toml
# System of 210,000 atoms
# - 70 ns/day (cycle0)
# - 30 ns/day (cycle1-)
