*********
Changelog
*********

v0.9.0
======

*   [docs] Switching styles (to furo), and making minor layout fixes.
*   Adding `Gacct`: very simple wrapper around  `sacct`. The output formatting might change in the future.

v0.7.0
======

*   Gps: switching to argparse
*   Ginfo: switching to argparse
*   Gdel: using `subprocess.run`
*   Gstat: using class to make reuse more efficient
*   Gdel: internally calling Gstat to print (removes a lot of duplicate code, and adds features)
*   Gstat: switching to argparse
*   Gstat: Adding "WorkDir" and "Dependency" to `--extra` option
*   `dummyslurm.sbatch`: Adding `--dependency` and `--chdir`
*   Adding `dummyslurm.scancel`
*   Adding `dummyslurm.sacct`: replacing text file with 'real' dummy command
*   Adding `dummyslurm.scontrol`
*   Adding `dummyslurm.squeue`
*   Adding `dummyslurm.sacct`
*   CI: extension of checks
*   Readme: adding badges
*   Fixing setup requirements

v0.6.1
======

*   Run jobs in serial sequence (#35)

v0.6.0
======

*   Switching to setuptools_scm
*   script: removing "SLURM_SUBMIT_DIR" (now dealt with in Gsub)

v0.5.1
======

*   Fixing version number

v0.5.0
======

*   API change Gsub:

    -   "--wait" -> "--delay"
    -   "--serial" -> "--wait"
    -   added "--constraint"

    To compile on different hardware e.g.:
    "Gsub --wait --constraint foo myscript.slurm && Gsub --wait --constraint bar myscript.slurm"

v0.4.0
======

*   Gsub: Adding serial option to wait until the previous job to finish.

v0.3.1
======

*   Updating formatting (of code and of docs)
*   Adding command-line tools to autodoc

v0.3.0
======

*   Gsub: adding status using YAML-file, allowing submit from YAML-file (#24)

v0.2.0
======

*   Bugfix: implementing --no-header options
*   Adding delay to Gsub
*   Adding tip to build once (using hardware optimization) (#22)
*   Updating gitignore
