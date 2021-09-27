import GooseSLURM as gs

# job-options
sbatch = {
    "job-name": "json",
    "out": "job.slurm.out",
    "nodes": 1,
    "ntasks": 1,
    "cpus-per-task": 1,
    "partition": "debug",
}

# command to run
command = """
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
"""

# write SLURM file
open("job.slurm", "w").write(gs.scripts.plain(command=command, **sbatch))
