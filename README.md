# GooseSLURM

[![](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE) 
[![](https://img.shields.io/badge/warranty-no-red.svg)](LICENSE) 
[![](https://img.shields.io/badge/download-.zip-lightgray.svg)](https://github.com/tdegeus/GooseSLURM/zipball/master) 
[![](https://img.shields.io/badge/download-.tar.gz-lightgray.svg)](https://github.com/tdegeus/GooseSLURM/tarball/master) 
[![](https://img.shields.io/badge/contact-tom@geus.me-blue.svg)](mailto:tom@geus.me) 
[![](https://img.shields.io/badge/contact-www.geus.me-blue.svg)](http://www.geus.me) 
[![](https://img.shields.io/badge/GitHub-tdegeus/GooseSLURM-blue.svg)](https://github.com/tdegeus/GooseSLURM)

This repository provides some command-line tools and some job-script for the SLURM queuing system.

<!-- MarkdownTOC -->

- [Command-line tools](#command-line-tools)
- [Batch scripts](#batch-scripts)
- [Installation](#installation)

<!-- /MarkdownTOC -->

# Command-line tools

* [Gstat](bin/Gstat): wrapper around `squeue`.
* [Ginfo](bin/Ginfo): wrapper around `sinfo`.
* [Gdel](bin/Gdel): delete some or all of the user's jobs.
* [Gscript](bin/Gscript): automatically write a job-script. The customizable part that involves running the job is provided as an option.
* [Gsub](bin/Gsub): submit a job from the folder of the job-script (essential for jobs that use a temporary directory).

# Batch scripts

* [tempdir](examples/tempdir): Exploit a temporary directory on the compute node to avoid costly read/write actions of the network.

    1.   Copy files to a temporary directory on the compute node
    2.   Run the job (while reading and writing locally on the compute node)
    3.   Copy all files back to the directory from which the job is submitted.

* [json_log](examples/json_log): Register some environment variables when the job starts. This particular examples shows a way to allow automatic copying from the [tempdir](examples/tempdir) back to the head node using [Gcopy](bin/Gcopy) while the job is running.

* [parallel](examples/parallel): Use GNU parallel to run several executables in parallel within a single job (that claims more that one CPU).

# Download

To download the script you could use git. 

1.  Login to the cluster:

    ```bash
    $ ssh username@url.to.cluster
    ```
    
2.  Clone this repository:

    ```bash
    $ cd /some/path
    $ git clone https://github.com/tdegeus/GooseSLURM.git
    ```
    
   GooseSLURM will then be downloaded to `/some/path/GooseSLURM`.

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
