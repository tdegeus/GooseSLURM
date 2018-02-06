# GooseSLURM

This repository provides some command-line tools and some job-script for the SLURM queuing system.

<!-- MarkdownTOC -->

- [Command-line tools](#command-line-tools)
- [Batch scripts](#batch-scripts)
- [Installation](#installation)

<!-- /MarkdownTOC -->

> **Disclaimer**
> 
> These tools and job-script reflect my personal approach and have not been reviewed by any system administrator or anyone from SLURM. They come with absolutely no warranty.
> 
>   (c - [MIT](https://github.com/tdegeus/GooseSLURM/blob/master/LICENSE)) T.W.J. de Geus (Tom) | tom@geus.me | www.geus.me | [github.com/tdegeus/GooseSLURM](https://github.com/tdegeus/GooseSLURM)

# Command-line tools

* [Gstat](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gstat): wrapper around `squeue`.
* [Ginfo](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Ginfo): wrapper around `sinfo`.
* [Gdel](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gdel): delete some or all of the user's jobs.
* [Gscript](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gscript): automatically write a job-script. The customizable part that involves running the job is provided as an option.
* [Gsub](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gsub): submit a job from the folder of the job-script (essential for jobs that use a temporary directory).

# Batch scripts

* [tempdir.slurm](https://github.com/tdegeus/GooseSLURM/blob/master/examples/tempdir/tempdir.slurm): copy files to `/tmp/${JOB_ID}` on the compute node, run the job, and copy all files back to the directory from which the job is submitted.

# Installation

To get these scripts to work one can:

-   Point the `$PATH` to the `bin/` folder of this directory, for example by adding the following line to the `~/.bashrc`:
  
    ```bash
    export PATH=/path/to/GooseSLURM/bin:$PATH
    ```
-   'Install' the script in your home folder:
  
    1.  Create a directory to store libraries in the home folder. For example:
  
        ```bash
        mkdir ~/opt
        ```

    2.  'Install' the GooseSLURM's scripts. For example
  
        ```bash
        cd /path/to/GooseSLURM
        mkdir build
        cd build
        cmake .. -DCMAKE_INSTALL_PREFIX:PATH=$HOME/opt
        make install
        ```
     
    3.  Make the `bin/` folder of this 'installation' directory locatable, by adding to the `~/.bashrc`:
 
        ```bash
        export PATH=$HOME/opt/bin:$PATH
        ```

> Note that one has to have Python3 (loaded), and the "[docopt](http://docopt.org)" library has to be available to Python. For example:
> 
> *   Load using
>  
>      ```bash
>      module load gcc/7.1.0 python/3.6.1
>      ```
>
>      Or something equivalent. Note that none of the feature should be very version dependent.
>      
> *    [Install "docopt"](https://pypi.python.org/pypi/docopt/) using
> 
>      ```bash
>      pip3 install --user docopt
>      ```
>
>      The `--user` option is only needed if you want to install the library to your own home-folder. On 'normal' systems this is typically not what you want to do, but it assumed here that you are doing this on a cluster where everything is shared.
