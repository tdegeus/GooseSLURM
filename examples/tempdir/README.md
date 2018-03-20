# tempdir

## Overview

 This script exploits a temporary directory on the compute node to avoid costly read/write actions of the network. 

 In particular it does the following:

1.   Copy files to a temporary directory on the compute node (which is in this case automatically provided by the queuing system).

2.   Run the job (while reading and writing locally on the compute node).

3.   Copy all files back to the directory from which the job is submitted (on the head node).

Here only items 1. and 3. use the network. During the computation all actions are local on the compute node.

## Code explained

The job script [`job.slurm`](/job.slurm)
