#!/bin/bash
set -e
module purge
module load gromacs

for trial in {1..1};
do
    pacs mdrun -f input.toml -t $trial
done

echo "pacsmd done" >&1
