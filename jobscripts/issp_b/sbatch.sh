#!/bin/bash
#SBATCH -N 6
#SBATCH -n 384
#SBATCH -c 2
#SBATCH -p B16cpu
#SBATCH --time=01:00:00

set -e
module purge

for trial in {1..1};
do
    pacs mdrun -f input.toml -t $trial
done

echo "pacsmd done" >&1
