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
>   (c - [MIT](blob/master/LICENSE)) T.W.J. de Geus (Tom) | tom@geus.me | www.geus.me | [github.com/tdegeus/GooseSLURM](https://github.com/tdegeus/GooseSLURM)

# Command-line tools

* [Gstat](blob/master/bin/Gstat): wrapper around `squeue`.
* [Ginfo](blob/master/bin/Ginfo): wrapper around `sinfo`.
* [Gdel](blob/master/bin/Gdel): delete some or all of the user's jobs.
* [Gscript](blob/master/bin/Gscript): automatically write a job-script. The customizable part that involves running the job is provided as an option.
* [Gsub](blob/master/bin/Gsub): submit a job from the folder of the job-script (essential for jobs that use a temporary directory).

# Batch scripts

* [tempdir](blob/master/examples/tempdir): exploit a temporary directory on the compute node to avoid costly read/write actions of the network.

    1.   Copy files to a temporary directory on the compute node
    2.   Run the job (while reading and writing locally on the compute node)
    3.   Copy all files back to the directory from which the job is submitted.

* [parallel](blob/master/examples/parallel/job.slurm): use GNU pap

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
