#!/bin/bash
#SBATCH --job-name job
#SBATCH --out job.slurm.out
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --partition debug

# 1. Define directory names [DO NOT CHANGE]
# =========================================

# get hostname
myhost=`hostname`

# get name of the temporary directory working directory, physically on the compute-node
workdir="$TMPDIR"

# get submit directory
# (every file/folder below this directory is copied to the compute node)
submitdir="${SLURM_SUBMIT_DIR}"

# 2. Write job info to a log file [MAY BE CHANGED/OMITTED]
# ========================================================

cat <<EOF > job.slurm.json
{
  "submitdir"           : "${submitdir}",
  "workdir"             : "${workdir}",
  "workdir_host"        : "${myhost}",
  "hostname"            : "${myhost}",
  "SLURM_SUBMIT_DIR"    : "${SLURM_SUBMIT_DIR}",
  "SLURM_JOB_ID"        : "${SLURM_JOB_ID}",
  "SLURM_JOB_NODELIST"  : "${SLURM_JOB_NODELIST}",
  "SLURM_SUBMIT_HOST"   : "${SLURM_SUBMIT_HOST}",
  "SLURM_JOB_NUM_NODES" : "${SLURM_JOB_NUM_NODES}",
  "SLURM_CPUS_PER_TASK" : "${SLURM_CPUS_PER_TASK}"
}
EOF

# 3. Transfer to node [DO NOT CHANGE]
# ===================================

# create/empty the temporary directory on the compute node
if [ ! -d "${workdir}" ]; then
  mkdir -p "${workdir}"
else
  rm -rf "${workdir}"/*
fi

# change current directory to the location of the sbatch command
# ("submitdir" is somewhere in the home directory on the head node)
cd "${submitdir}"
# copy all files/folders in "submitdir" to "workdir"
# ("workdir" == temporary directory on the compute node)
cp -prf * ${workdir}
# change directory to the temporary directory on the compute-node
cd ${workdir}

# 4. Function to transfer back to the head node [DO NOT CHANGE]
# =============================================================

# define clean-up function
function clean_up {
  # - change directory to the location of the sbatch command (on the head node)
  cd "${submitdir}"
  # - copy everything from the temporary directory on the compute-node
  cp -prf "${workdir}"/* .
  # - erase the temporary directory from the compute-node
  rm -rf "${workdir}"/*
  rm -rf "${workdir}"
  # - exit the script
  exit
}

# call "clean_up" function when this script exits, it is run even if SLURM cancels the job
trap 'clean_up' EXIT

# 5. Execute [MODIFY COMPLETELY TO YOUR NEEDS]
# ============================================

# simplest example in the world, sleep a bit to allow a bit of monitoring
echo "hello world" > "test.log"
sleep 10
