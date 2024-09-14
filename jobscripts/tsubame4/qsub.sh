#!/bin/bash
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N pacsmd_test

set -e
. /etc/profile.d/modules.sh

module purge
module load openmpi/5.0.2-gcc
module load gromacs/2024

# Please activate the python environment in which you can use pacsmd library
# Change the path to your environment
# source /home/x/xxxxxxx/anaconda3/etc/profile.d/conda.sh
# conda activate pacs

for trial in {1..1};
do
    pacs mdrun -f input.toml -t $trial
done

echo "pacsmd done" >&1

# Simulation speed measured by this script and the corresponding .toml
# System of 300,000 atoms
# - 100 ns/day
