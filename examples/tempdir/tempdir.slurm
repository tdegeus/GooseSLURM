#!/bin/bash
#SBATCH --job-name tempdir
#SBATCH --out tempdir.slurm.out
#SBATCH --error tempdir.slurm.error
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

# store submit directory
# (every file/folder below this directory is copied to the compute-node)
submitdir="${SLURM_SUBMIT_DIR}"

# (ii) Write job-info to a log-file [MAY BE CHANDED/OMITTED]
# ==========================================================

cat <<EOF > tempdir.slurm.json
{
  "workdir"             : "${workdir}",
  "submitdir"           : "${submitdir}",
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
# ("submitdir" is somewhere in the home directory on the head-node)
cd "${submitdir}"
# copy all files/folders in "submitdir" to "workdir"
# ("workdir" == temporary directory on the compute-node)
cp -prf * ${workdir}
# change directory to the temporary directory on the compute-node
cd ${workdir}

# 2. Execute [MODIFY COMPLETELY TO YOUR NEED]
# ===========================================

# set the number of CPUs to be used by an OpenMP application
export OMP_NUM_THREADS=${SLURM_CPUS_ON_NODE}

# simplest example in the world, sleep a bit to allow a bit of monitoring
echo "hello world"
sleep 10

# 3. Transfer back to the head-node [DO NOT CHANGE]
# =================================================

# change directory to the location of the sbatch-command (on the head-node)
cd "${submitdir}"
# copy everything from the temporary directory on the compute-node
cp -prf "${workdir}"/* .
# erase the temporary directory from the compute-node
rm -rf "${workdir}"
