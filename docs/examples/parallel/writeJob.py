import GooseSLURM as gs

# job-options
sbatch = {
    "job-name": "parallel",
    "out": "job.slurm.out",
    "nodes": 1,
    "ntasks": 1,
    "cpus-per-task": 5,
    "partition": "debug",
}

# command to run
command = "parallel --max-procs=${SLURM_CPUS_PER_TASK} 'echo {1} {2}' ::: {1..12} ::: summer winter"

# write SLURM file
open("job.slurm", "w").write(gs.scripts.plain(command=command, **sbatch))
