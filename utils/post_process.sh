#!/bin/bash

set -e 

<< TODO
fit to prd_rmmol_fit.xtc
genrepresent
gencom (trial, genrepresent)
genfeature (comdist, comvec) for each trial
TODO

# source the conda environment
# source (anaconda3_dir)/etc/profile.d/conda.sh
# conda activate pacstk

export PYTHONWARNINGS=ignore

# define the trials
all_trials=(`seq -w 01 30`)
last_trial=${all_trials[${#all_trials[@]}-1]}
n_paras=15


echo "all_trials: ${all_trials[@]}"
echo "n_paras: $n_paras"

# define the selections
# change the selections according to the system
s1="protein and name CA" # selection for protein backbone
s2="resname LIG" # selection for ligand
top="trial001/cycle000/replica001/rmmol_top.pdb"
gencom_dir="gencom"
genrep_dir="genrep"


# prepare
mkdir -p $gencom_dir
mkdir -p $genrep_dir


# fit
for i in ${all_trials[@]}; do
    pacs fit trial mdtraj -t $i -tf prd_rmmol.xtc \
    -top $top \
    -r $top \
    -ts "$s1" -rs "$s1" \
    -p ${n_paras} -o prd_rmmol_fit.xtc 
done


# genrepresent
for i in ${all_trials[@]}; do
    pacs genrepresent gmx -t $i -trj prd_rmmol_fit.xtc \
    -top $top -g gmx_mpi
done

## gather representitive trajectory to the genrep directory
for trial in ${all_trials[@]}; do
    trial_str=$(printf "%03d" $trial)
    cp trial$trial/genrepresent/repr_complete.xtc genrep/t${trial_str}_rep.xtc
done


# gencom
## for the representative trajectory
for i in ${all_trials[@]}; do
    pacs gencom traj mdtraj -trj trial0$i/genrepresent/repr_complete.xtc \
    -top $top -r $i -s "$s2" -o $gencom_dir/rep_pathway_$i.pdb 
done

## for the all trajectories
## this part takes a long time (~1-2 hours per trial)
n_runs=0
for i in ${all_trials[@]}; do
    if [[ $n_runs -lt $(($n_paras - 1)) && $i != $last_trial ]]; then
        pacs gencom trial mdtraj -t $i -trj prd_rmmol_fit.xtc \
        -top $top -r $i -s "$s2" -o $gencom_dir/pathway_$i.pdb -sf 10 &
        ((n_runs++))
    else
        pacs gencom trial mdtraj -t $i -trj prd_rmmol_fit.xtc \
        -top $top -r $i -s "$s2" -o $gencom_dir/pathway_$i.pdb -sf 10
        n_runs=0
    fi
done


# genfeature
## inter-com distance
for i in ${all_trials[@]}; do
    pacs genfeature comdist mdtraj -t $i -tf prd_rmmol_fit.xtc \
        -top $top -p ${n_paras} -s1 "$s1"  -s2 "$s2"
done

## inter-com vector
for i in ${all_trials[@]}; do
    pacs genfeature comvec mdtraj -t $i -tf prd_rmmol_fit.xtc \
    -ref $top  -ft "$s1" -fr "$s1" \
    -top $top -p ${n_paras} -s1 "$s1"  -s2 "$s2"
done
