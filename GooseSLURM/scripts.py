from . import duration
from . import memory


def plain(
    command=[],
    shell="#!/bin/bash -l",
    **sbatch,
):
    r"""
    Return simple SBATCH-file (as text).

    :options:

        **command** (``<str>`` | ``<list>``)
            Command(s) to execute.
            If the input is a list each entry is included as an individual line.

        **shell** (``<str>``)
            The shell to use.

    :SBATCH options:

        **mem** (``<int>`` | ``<str>``)
            Memory claim (may be human readable, see ``GooseSLUM.memory.asSlurm``).

        **time**  (``<str>``)
            Wall-time claim (may be human readable, see ``GooseSLUM.duration.asSlurm``).

        **out** (``<str``>)
            Name of the output file, e.g. ``myjob_%j.out``.

        ...
    """

    # convert to string (if needed)
    if not isinstance(command, str):
        command = "\n".join(command)

    # convert sbatch options
    for key, item in sbatch.items():
        if key in ["time"]:
            sbatch[key] = duration.asSlurm(item)
        if key in ["mem"]:
            sbatch[key] = memory.asSlurm(item)

    # - convert to string
    sbatch = "\n".join(
        [f"#SBATCH --{key:s} {str(arg):s}" for key, arg in sbatch.items()]
    )

    return """{shell:s}
{sbatch:s}

{command:s}
  """.format(
        shell=shell,
        sbatch=sbatch,
        command=command,
    )


def tempdir(remove=[], command=[], shell="#!/bin/bash -l", **sbatch):
    r"""
    Return SBATCH-file (as text) that uses a temporary working directory on the compute node.

    :options:

        **remove** (``<list>``)
            List with files/folders to remove from the temporary directory before copying.

        **command** (``<str>`` | ``<list>``)
            Command(s) to execute.
            If the input is a list each entry is included as an individual line.

        **shell** (``<str>``)
            The shell to use.

    :SBATCH options:

        **mem** (``<int>`` | ``<str>``)
            Memory claim (may be human readable, see ``GooseSLUM.memory.asSlurm``).

        **time**  (``<str>``)
            Wall-time claim (may be human readable, see ``GooseSLUM.duration.asSlurm``).

        **out** (``<str``>)
            Name of the output file, e.g. ``myjob_%j.out``.

        ...
    """

    # convert to string
    if len(remove) > 0:
        remove = "rm -r " + " ".join(remove)
    else:
        remove = "# rm -r ..."

    # convert to string (if needed)
    if not isinstance(command, str):
        command = "\n".join(command)

    # convert sbatch options
    for key, item in sbatch.items():
        if key in ["time"]:
            sbatch[key] = duration.asSlurm(item)
        if key in ["mem"]:
            sbatch[key] = memory.asSlurm(item)

    # extract name of the output file
    outfile = sbatch["out"]

    # - convert to string
    sbatch = "\n".join(
        [f"#SBATCH --{key:s} {str(arg):s}" for key, arg in sbatch.items()]
    )

    return """{shell:s}
{sbatch:s}

# I. Define directory names [DO NOT CHANGE]
# =========================================

# get name of the temporary directory working directory, physically on the compute-node
workdir="${{TMPDIR}}"

# get current directory
# (every file/folder below this directory is copied to the compute node)
submitdir="$(pwd)"

# 1. Transfer to node [DO NOT CHANGE]
# ===================================

# create/empty the temporary directory on the compute node
if [ ! -d "${{workdir}}" ]; then
  mkdir -p "${{workdir}}"
else
  rm -rf "${{workdir}}"/*
fi

# change current directory to the location of the sbatch command
# ("submitdir" is somewhere in the home directory on the head node)
cd "${{submitdir}}"
# copy all files/folders in "submitdir" to "workdir"
# ("workdir" == temporary directory on the compute node)
cp -prf * ${{workdir}}
# change directory to the temporary directory on the compute-node
cd ${{workdir}}

# 3. Function to transfer back to the head node [DO NOT CHANGE]
# =============================================================

# define clean-up function
function clean_up {{
  # - remove log-file on the compute-node, to avoid the one created by SLURM is overwritten
  rm {outfile:s}
  # - delete temporary files from the compute-node, before copying
  {remove:s}
  # - change directory to the location of the sbatch command (on the head node)
  cd "${{submitdir}}"
  # - copy everything from the temporary directory on the compute-node
  cp -prf "${{workdir}}"/* .
  # - erase the temporary directory from the compute-node
  rm -rf "${{workdir}}"/*
  rm -rf "${{workdir}}"
  # - exit the script
  exit
}}

# call "clean_up" function when this script exits, it is run even if SLURM cancels the job
trap 'clean_up' EXIT

# 2. Execute [MODIFY COMPLETELY TO YOUR NEEDS]
# ============================================

{command:s}
  """.format(
        shell=shell,
        sbatch=sbatch,
        command=command,
        outfile=outfile,
        remove=remove,
    )
