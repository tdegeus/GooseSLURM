#!/bin/bash
#SBATCH --job-name scratch
#SBATCH --out scratch.slurm.out
#SBATCH --error scratch.slurm.out
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --mem 4096
#SBATCH --time 12:30:00

# (i) Generate unique directory name [DO NOT CHANGE]
# ==================================================

# store my username
username=`whoami`

# set the name of the temporary directory on the compute-node
# use job-id to create a unique folder
workdir="/scratch/$username/${SLURM_JOB_ID}"

# (ii) Write job-info to a log-file [CHANGE TO YOUR NEED]
# =======================================================

cat <<EOF > scratch.slurm.json
{
  "workdir"             : "${workdir}",
  "submitdir"           : "${SLURM_SUBMIT_DIR}",
  "SLURM_SUBMIT_DIR"    : "${SLURM_SUBMIT_DIR}",
  "SLURM_JOB_ID"        : "${SLURM_JOB_ID}",
  "SLURM_JOB_NODELIST"  : "${SLURM_JOB_NODELIST}",
  "SLURM_SUBMIT_HOST"   : "${SLURM_SUBMIT_HOST}",
  "SLURM_JOB_NUM_NODES" : "${SLURM_JOB_NUM_NODES}",
  "SLURM_CPUS_ON_NODE"  : "${SLURM_CPUS_ON_NODE}"
}
EOF

# 1. Transfer to node [DO NOT CHANGE]
# ===================================

# create/empty the temporary directory on the compute-node
if [ ! -d "${workdir}" ]; then
  mkdir -p "${workdir}"
else
  rm -rf "${workdir}"/*
fi

# change current directory to the location of the sbatch-command
# (in the home directory on the head-node)
cd "${SLURM_SUBMIT_DIR}"
# copy all files/folders in the directory of the sbatch-command
cp -prf * ${workdir}
# change directory to the temporary directory on the compute-node
cd ${workdir}

# 2. Execute [MODIFY TO YOUR NEED]
# ================================

# a simple script (replace by your commands)
echo "Job ID: " > "scratch.slurm.log"
echo "${SLURM_JOB_ID}" >> "scratch.slurm.log"
echo "" >> "scratch.slurm.log"
echo "Host name: " >> "scratch.slurm.log"
echo `hostname` >> "scratch.slurm.log"
echo "" >> "scratch.slurm.log"
echo "Current directory: " >> "scratch.slurm.log"
echo `pwd` >> "scratch.slurm.log"
echo "" >> "scratch.slurm.log"
echo "Directory contents: " >> "scratch.slurm.log"
echo `ls` >> "scratch.slurm.log"

sleep 5

# 3. Transfer back to the head-node [DO NOT CHANGE]
# =================================================

# change directory to the location of the sbatch-command (on the head-node)
cd "${SLURM_SUBMIT_DIR}"
# copy everything from the temporary directory on the compute-node
cp -prf "${workdir}"/* .
# erase the temporary directory from the compute-node
rm -rf "${workdir}"
