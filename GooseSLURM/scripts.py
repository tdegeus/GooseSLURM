
from . import duration
from . import memory

# ==================================================================================================

def tempdir(filename='job.slurm', remove=[], command=[], **sbatch):
  r'''
Return SBATCH-file (as text) that uses a temporary working directory on the compute node.

:options:

  **filename** (``<str>`` | [``'job.slurm'``])
    The filename base to store the out and JSON files.

  **remove** (``<list>``)
    List with files/folders to remove from the temporary directory before copying.

  **command** (``<str>`` | ``<list>``)
    Command(s) to execute. If the input is a list each entry is included as an individual line.

:SBATCH options:

  **mem** (``<int>`` | ``<str>``)
    Memory claim (may be human readable, see 'GooseSLUM.memory.asSlurm').

  **time**  (``<str>``)
    Wall-time claim (may be human readable, see 'GooseSLUM.time.asSlurm').

  **out** ([``filename+'.out'``] | ``<str``>)
    Name of the output file.

  ...
  '''

  # convert to string
  if len(remove) > 0: remove = 'rm -r ' + ' '.join(remove)
  else              : remove = '# rm -r ...'

  # convert to string (if needed)
  if type(command) != str:
    command = '\n'.join(command)

  # convert sbatch options
  # - change format
  for key, item in sbatch.items():
    if key in ['time']: sbatch[key] = duration.asSlurm(item)
    if key in ['mem' ]: sbatch[key] = memory  .asSlurm(item)
  # - add defaults
  sbatch.setdefault('out', filename+'.out')

  # extract name of the output file
  outfile = sbatch['out']

  # - convert to string
  sbatch = '\n'.join(['#SBATCH --{0:s} {1:s}'.format(key,str(arg)) for key,arg in sbatch.items()])

  return '''#!/bin/bash
{sbatch:s}

# I. Define directory names [DO NOT CHANGE]
# =========================================

# get name of the temporary directory working directory, physically on the compute-node
workdir="${{TMPDIR}}"

# get submit directory
# (every file/folder below this directory is copied to the compute node)
submitdir="${{SLURM_SUBMIT_DIR}}"

# II. Write job info to a log file [MAY BE CHANGED/OMITTED]
# =========================================================

# get hostname
myhost=`hostname`

# write JSON-file
cat <<EOF > {filename:s}.json
{{
  "submitdir"           : "${{submitdir}}",
  "workdir"             : "${{workdir}}",
  "workdir_host"        : "${{myhost}}",
  "hostname"            : "${{myhost}}",
  "SLURM_SUBMIT_DIR"    : "${{SLURM_SUBMIT_DIR}}",
  "SLURM_JOB_ID"        : "${{SLURM_JOB_ID}}",
  "SLURM_JOB_NODELIST"  : "${{SLURM_JOB_NODELIST}}",
  "SLURM_SUBMIT_HOST"   : "${{SLURM_SUBMIT_HOST}}",
  "SLURM_JOB_NUM_NODES" : "${{SLURM_JOB_NUM_NODES}}",
  "SLURM_CPUS_PER_TASK" : "${{SLURM_CPUS_PER_TASK}}"
}}
EOF

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
  '''.format(
    sbatch   = sbatch,
    filename = filename,
    command  = command,
    outfile  = outfile,
    remove   = remove,
  )

# ==================================================================================================

def plain(filename='job.slurm', command=[], cd_submitdir=True, **sbatch):
  r'''
Return SBATCH-file (as text) that uses a temporary working directory on the compute node.

:options:

  **filename** (``<str>`` | [``'job.slurm'``])
    The filename base to store the out and JSON files.

  **command** (``<str>`` | ``<list>``)
    Command(s) to execute. If the input is a list each entry is included as an individual line.

  **cd_submitdir** ([``True``] | ``False``)
    Include 'cd "${SLURM_SUBMIT_DIR}"' at the beginning of the script.

:SBATCH options:

  **mem** (``<int>`` | ``<str>``)
    Memory claim (may be human readable, see 'GooseSLUM.memory.asSlurm').

  **time**  (``<str>``)
    Wall-time claim (may be human readable, see 'GooseSLUM.time.asSlurm').

  **out** ([``filename+'.out'``] | ``<str``>)
    Name of the output file.

  ...
  '''

  # convert to string (if needed)
  if type(command) != str:
    command = '\n'.join(command)

  # add command
  if cd_submitdir:

    command = '\n' + command
    command = 'cd "${SLURM_SUBMIT_DIR}"\n' + command
    command = '# change current directory to the location of the sbatch command\n' + command

  # convert sbatch options
  # - change format
  for key, item in sbatch.items():
    if key in ['time']: sbatch[key] = duration.asSlurm(item)
    if key in ['mem' ]: sbatch[key] = memory  .asSlurm(item)
  # - add defaults
  sbatch.setdefault('out', filename+'.out')

  # - convert to string
  sbatch = '\n'.join(['#SBATCH --{0:s} {1:s}'.format(key,str(arg)) for key,arg in sbatch.items()])

  return '''#!/bin/bash
{sbatch:s}

{command:s}

  '''.format(
    sbatch   = sbatch,
    filename = filename,
    command  = command,
  )

# ==================================================================================================

