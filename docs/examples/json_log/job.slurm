#!/bin/bash
#SBATCH --job-name json
#SBATCH --out job.slurm.out
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --partition debug

# Write job info to a JSON-log file
# =================================

# get hostname
myhost=`hostname`

# write log file
cat <<EOF > job.slurm.json
{
  "hostname"            : "${myhost}",
  "SLURM_SUBMIT_DIR"    : "${SLURM_SUBMIT_DIR}",
  "SLURM_JOB_ID"        : "${SLURM_JOB_ID}",
  "SLURM_JOB_NODELIST"  : "${SLURM_JOB_NODELIST}",
  "SLURM_SUBMIT_HOST"   : "${SLURM_SUBMIT_HOST}",
  "SLURM_JOB_NUM_NODES" : "${SLURM_JOB_NUM_NODES}",
  "SLURM_CPUS_PER_TASK" : "${SLURM_CPUS_PER_TASK}"
}
EOF

# Execute
# =======

# simplest example in the world, sleep a bit to allow a bit of monitoring
echo "hello world" > "test.log"
sleep 10
