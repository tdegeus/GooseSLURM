#!/bin/bash
#SBATCH --job-name parallel
#SBATCH --out job.slurm.out
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 5
#SBATCH --partition debug

parallel --max-procs=${SLURM_CPUS_PER_TASK} 'echo {1} {2}' ::: {1..12} ::: summer winter
