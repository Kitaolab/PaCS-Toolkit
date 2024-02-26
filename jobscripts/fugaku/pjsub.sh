#!/bin/bash
#PJM -L "node=5"
#PJM -L "rscgrp=small"
#PJM -L "elapse=00:30:00"
#PJM --mpi "max-proc-per-node=4"
#PJM -g <groupname>
#PJM -x PJM_LLIO_GFSCACHE=/vol0004
#PJM -S

. /vol0004/apps/oss/spack/share/spack/setup-env.sh
spack load gromacs@2023.2
spack load /23rofh6

export OMP_NUM_THREADS=12
path_to_pacstk="/path/to/pacstk"

ln -s $path_to_pacsmd ./.

for trial in {1..1};
do
    python3 -m pacs mdrun -f input.toml -t $trial
done

echo "pacsmd done" >&1
