#!/bin/bash
#SBATCH --job-name scratch
#SBATCH --out scratch.out
#SBATCH --error scratch.out
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --mem 4096
#SBATCH --time 12:30:00

# Generate unique directory name [DO NOT CHANGE]
# ==============================================

# store my username
username=`whoami`

# set the name of the temporary directory on the compute-node
# use job-id to create a unique folder
computedir="/scratch/$username/${SLURM_JOB_ID}"

# 1. Transfer to node [DO NOT CHANGE]
# ===================================

# create/empty the temporary directory on the compute-node
if [ ! -d "${computedir}" ]; then
  mkdir -p "${computedir}"
else
  rm -rf "${computedir}"/*
fi

# change current directory to the location of the sbatch-command
# (in the home directory on the head-node)
cd "${SLURM_SUBMIT_DIR}"
# copy all files/folders in the directory of the sbatch-command
cp -prf * ${computedir}
# change directory to the temporary directory on the compute-node
cd ${computedir}

# 2. Execute [MODIFY TO YOUR NEED]
# ================================

# a simple script (replace by your commands)
echo "Job ID: " > "scratch.log"
echo "${SLURM_JOB_ID}" >> "scratch.log"
echo "" >> "scratch.log"
echo "Host name: " >> "scratch.log"
echo `hostname` >> "scratch.log"
echo "" >> "scratch.log"
echo "Current directory: " >> "scratch.log"
echo `pwd` >> "scratch.log"
echo "" >> "scratch.log"
echo "Directory contents: " >> "scratch.log"
echo `ls` >> "scratch.log"

sleep 5

# 3. Transfer back to the head-node [DO NOT CHANGE]
# =================================================

# change directory to the location of the sbatch-command (on the head-node)
cd "${SLURM_SUBMIT_DIR}"
# copy everything from the temporary directory on the compute-node
cp -prf "${computedir}"/* .
# erase the temporary directory from the compute-node
rm -rf "${computedir}"
