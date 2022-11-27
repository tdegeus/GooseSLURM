r"""Gsub
    Submit job-scripts and add the "--chdir" option
    to run the scripts from the directory in with the sbatch-file is stored.
    See https://slurm.schedmd.com/sbatch.html

Usage:
    Gsub [options] <files>...

Arguments:
    Job-scripts.

Options:
    --dry-run
        Print commands to screen, without executing.

    --verbose
        Verbose all commands and their output.

    -Q, --quiet
        Do no show progress-bar.

    --log = FILENAME
        Log the JobIDs to a YAML-file (updated after each submit).
        Existing log files are appended.

    --delay = FLOAT
        Seconds to wait between submitting jobs. [default: 0.1]

    -r, --repeat = INT
        Submit using dependencies such that the job will be repeated 'n' times. [default: 1]

    --serial
        Submit using dependencies such that jobs are run after each other.

    -A, --account = ARG (sbatch option)
        Account name.

    -b, --begin = ARG (sbatch option)
        Allocate at the later time.
        E.g. ``--begin=now+1hour``.

    --comment = ARG (sbatch option)
        Arbitrary comment.

    -c, --constraint = ARG (sbatch option)
        Nodes can have features assigned to them by the Slurm administrator.

    -d, --dependency = ARG (sbatch option)
        Defer the start of this job until the specified dependencies have been satisfied completed.

    -X, --exclude = ARG (sbatch option)
        Exclude nodes.

    --export = ARG (sbatch option)
        Export environment variables.

    --mem = ARG (sbatch option)
        Memory allocation.

    -w, --wait (sbatch option)
        Do not exit until the submitted job terminates.

    -h, --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""
import argparse
import os
import re
import subprocess
import time

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

    return int(re.split(r"(Submitted batch job)([\ ]*)([0-9]*)(.*)", out)[3])


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
    class Parser(argparse.ArgumentParser):
        def print_help(self):
            print(__doc__)

    parser = Parser()
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("-Q", "--quiet", action="store_true")
    parser.add_argument("-l", "--log", type=str)
    parser.add_argument("--delay", type=float, default=0.1)
    parser.add_argument("-r", "--repeat", type=int, default=1)
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("-A", "--account", type=str)
    parser.add_argument("-b", "--begin", type=str)
    parser.add_argument("--comment", type=str)
    parser.add_argument("-c", "--constraint", type=str)
    parser.add_argument("-d", "--dependency", type=str)
    parser.add_argument("-X", "--exclude", type=str)
    parser.add_argument("--export", type=str)
    parser.add_argument("--mem", type=str)
    parser.add_argument("-w", "--wait", action="store_true")

    parser.add_argument("files", nargs="*", type=str)
    args = parser.parse_args()
    dargs = vars(args)
    down = ["account", "begin", "comment", "constraint", "dependency", "exclude", "export", "mem"]

    log = read_log(args.files, args.log)
    jobid = ""

    for filename in args.files:
        if not os.path.isfile(filename):
            raise OSError(f'"{filename}" does not exist')

    pbar = tqdm.tqdm(args.files, disable=args.quiet)

    for ifile, file in enumerate(pbar):
        for rep in range(int(args.repeat)):
            pbar.set_description(file)
            path, name = os.path.split(file)
            options = ["--chdir", os.path.abspath(path)]
            if args.wait:
                options += ["--wait"]
            for opt in down:
                if dargs[opt]:
                    options += [f"--{opt:s}", dargs[opt]]
            if rep or (args.serial and ifile):
                options += ["--dependency", str(jobid)]
            options += [name]
            jobid = sbatch(options, verbose=args.verbose, dry_run=args.dry_run)
            log[file] += [jobid]
            if args.log:
                fileio.YamlDump(args.log, log)
            time.sleep(float(args.delay))
