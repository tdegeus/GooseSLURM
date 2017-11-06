# GooseSLURM

This repository provides some command-line tools and some batch scripts for the SLURM queuing system.

> These tools and batch scripts reflect my personal approach and have not been reviewed by any system administrator or anyone from SLURM. They come with absolutely no warranty.
> 
>   (c - [MIT](https://github.com/tdegeus/GooseSLURM/blob/master/LICENSE)) T.W.J. de Geus (Tom) | tom@geus.me | www.geus.me | [github.com/tdegeus/GooseSLURM](https://github.com/tdegeus/GooseSLURM)

## Command-line tools

* [Gstat](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gstat): wrapper around `squeue`.
* [Gsub](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gsub): automatically write a batch script and submit the job, for some common job based on an executable that runs an input file.
* [Gdel](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gdel): delete a set or all of the user's jobs.

## Batch scripts

* [heavy-io.slurm](https://github.com/tdegeus/GooseSLURM/blob/master/examples/heavy-io.slurm): copy files to `/scratch`, run the job, and copy all files back to the home-directory.


