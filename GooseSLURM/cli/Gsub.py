r"""Gsub
    Submit job-scripts and add the "--chdir" option
    to run the scripts from the directory in with the sbatch-file is stored.

Usage:
    Gsub [options] <files>...

Arguments:
    Job-scripts.

Options:
    --dry-run
        Print commands to screen, without executing.

    --verbose
        Verbose all commands and their output.

    --log=N
        Log the JobIDs to a YAML-file (updated after each submit).
        Existing log files are appended.

    --delay=N
        Seconds to wait between submitting jobs. [default: 0.1]

    -r, --repeat=N
        Submit using dependencies such that the job will be repeated 'n' times. [default: 1]

    -d, --dependency=N
        (sbatch option) Defer the start of this job until the specified dependencies
        have been satisfied completed.

    -w, --wait
        (sbatch option) Do not exit until the submitted job terminates..

    -c, --constraint=N
        (sbatch option) Nodes can have features assigned to them by the Slurm administrator.

    -Q, --quiet
        Do no show progress-bar.

    -h, --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""
import os
import subprocess
import time

import docopt
import tqdm

from .. import fileio
from .. import version


def sbatch(options, verbose=False, dry_run=False):
    """
    Submit job and return the job-id.
    """

    assert type(options) == list

    if dry_run or verbose:
        print(" ".join(["sbatch"] + options))

    if dry_run:
        return None

    out = subprocess.check_output(["sbatch"] + options).decode("utf-8")

    if verbose:
        print(out, end="")

    return out.split("\n")[0].split("Submitted batch job ")[1]


def read_log(files, logfile=None):
    """
    Read existing log-file.
    If the file does not exists an empty log is returned.

    :param files: List of files to submit.
    :param logfile: Filename of the log-file.
    :return: Log as dict.
    """

    log = {filename: [] for filename in files}

    if logfile is None:
        return log

    if not os.path.isfile(os.path.realpath(logfile)):
        return log

    log = fileio.YamlRead(logfile)

    if type(log) != dict:
        raise OSError("Unable to interpret log file")

    for filename in files:
        if filename not in log:
            raise OSError(f'"{filename} not in log file"')
        if type(log[filename]) != list:
            raise OSError(f'Log of "{filename}" not interpretable')

    return log


def main():

    args = docopt.docopt(__doc__, version=version)
    files = args["<files>"]
    log = read_log(files, args["--log"])
    jobid = ""

    for filename in files:
        if not os.path.isfile(filename):
            raise OSError(f'"{filename}" does not exist')

    pbar = tqdm.tqdm(files, disable=args["--quiet"])

    for ifile, file in enumerate(pbar):
        for rep in range(int(args["--repeat"])):
            pbar.set_description(file)
            path, name = os.path.split(file)
            options = [f"--chdir {os.path.abspath(path):s}"]
            if args["--wait"]:
                options += ["--wait"]
            for opt in ["--constraint", "--dependency"]:
                if args[opt]:
                    options += [f"{opt:s} {args[opt]:s}"]
            if rep:
                options += [f"--dependency {jobid}"]
            options += [name]
            jobid = sbatch(
                options, verbose=args["--verbose"], dry_run=args["--dry-run"]
            )
            log[file] += [jobid]
            if args["--log"]:
                fileio.YamlDump(args["--log"], log)
            time.sleep(float(args["--delay"]))
