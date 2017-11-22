# GooseSLURM

This repository provides some command-line tools and some batch scripts for the SLURM queuing system.

> These tools and batch scripts reflect my personal approach and have not been reviewed by any system administrator or anyone from SLURM. They come with absolutely no warranty.
> 
>   (c - [MIT](https://github.com/tdegeus/GooseSLURM/blob/master/LICENSE)) T.W.J. de Geus (Tom) | tom@geus.me | www.geus.me | [github.com/tdegeus/GooseSLURM](https://github.com/tdegeus/GooseSLURM)

# Contents

<!-- MarkdownTOC -->

- [Overview](#overview)
    - [Command-line tools](#command-line-tools)
    - [Batch scripts](#batch-scripts)
- [Installation](#installation)

<!-- /MarkdownTOC -->

# Overview

## Command-line tools

* [Gstat](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gstat): wrapper around `squeue`.
* [Gsub](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gsub): automatically write a batch script and submit the job, for some common job based on an executable that runs an input file.
* [Gdel](https://github.com/tdegeus/GooseSLURM/blob/master/bin/Gdel): delete a set or all of the user's jobs.

## Batch scripts

* [heavy-io.slurm](https://github.com/tdegeus/GooseSLURM/blob/master/examples/heavy-io.slurm): copy files to `/scratch`, run the job, and copy all files back to the home-directory.

# Installation

To get these scripts to work one can:

-   Point the `$PATH` to the `bin/` folder of this directory, for example by adding the following line to the `~/.bashrc`:
  
    ```bash
    export PATH=/path/to/GooseSLURM/bin:$PATH
    ```
-   'Install' the script in your home folder:
  
    1.  Create a directory to store libraries in the home-folder. For example:
  
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

> Note that one has to have Python 3 (loaded).
