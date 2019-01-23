#!/bin/bash

#SBATCH -J G16_test
#SBATCH --partition=amd
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4
#SBATCH --mem=3145728KB

ID=$SLURM_JOB_ID
export g16root=/opt/shared
export GAUSS_SCRDIR=/scratch/${ID}

. $g16root/g16/bsd/g16.profile
mkdir $GAUSS_SCRDIR
cp -p * $GAUSS_SCRDIR/
cd $GAUSS_SCRDIR
mkdir -p $SLURM_SUBMIT_DIR
g16 < input_sp.dat > $SLURM_SUBMIT_DIR/out.dat
cp -rp * $SLURM_SUBMIT_DIR
cd $SLURM_SUBMIT_DIR
rm -rf $GAUSS_SCRDIR

