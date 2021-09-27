import GooseSLURM as gs

# job-options
sbatch = {
    "job-name": "tempdir",
    "out": "job.slurm.out",
    "nodes": 1,
    "ntasks": 1,
    "cpus-per-task": 1,
    "partition": "debug",
}

# command to run
command = """
# simplest example in the world, sleep a bit to allow a bit of monitoring
echo "hello world" > "test.log"
sleep 10
"""

# write SLURM file
open("job.slurm", "w").write(gs.scripts.tempdir(command=command, **sbatch))
