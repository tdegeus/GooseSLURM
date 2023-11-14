import re
import subprocess

from . import duration
from . import fileio
from . import files
from . import memory
from . import ps
from . import rich
from . import sacct
from . import scripts
from . import sinfo
from . import squeue
from . import table
from ._version import version
from ._version import version_tuple
from .cli.Gstat import main as Gstat
from .cli.Gsub import main as Gsub


def sbatch(options, verbose=False, dry_run=False):
    """
    Submit job and return the job-id.
    """

    assert isinstance(options, list)

    if dry_run or verbose:
        print(" ".join(["sbatch"] + options))

    if dry_run:
        return None

    out = subprocess.check_output(["sbatch"] + options).decode("utf-8")

    if verbose:
        print(out, end="")

    return int(re.split(r"(Submitted batch job)([\ ]*)([0-9]*)(.*)", out)[3])
