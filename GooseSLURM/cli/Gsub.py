r"""Gsub
    Submit job-scripts from their directory.

Usage:
    Gsub [options] --input=N
    Gsub [options] <files>...

Arguments:
    Job-scripts.

Options:
    --dry-run
        Print commands to screen, without executing.

    --verbose
        Verbose all commands and their output.

    -i, --input=N
        Submit job-scripts stored in YAML-file.

    -k, --key=N
        Path in the input YAML-file, separated by "/". [default: /]

    -o, --output=N
        Output submitted/pending job-scripts to YAML-file (updated after each submit).

    -d, --delay=N
        Seconds to wait between submitting jobs. [default: 0.1]

    -w, --wait
        (sbatch option) Do not exit until the submitted job terminates..

    -c, --constraint=N
        (sbatch option) Nodes can have features assigned to them by the Slurm administrator.

    -q, --quiet
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

from .. import version
from .. import fileio


def run(cmd, verbose=False, dry_run=False):

    if dry_run:
        print(cmd)
        return None

    out = subprocess.check_output(cmd, shell=True).decode("utf-8")

    if verbose:
        print(cmd)
        print(out, end="")

    return out


def dump(files, ifile, outname):

    if not outname:
        return

    data = {
        "submitted": [files[i] for i in range(ifile)],
        "pending": [files[i] for i in range(ifile, len(files))],
    }

    fileio.YamlDump(outname, data)


def main():

    # parse command-line options
    args = docopt.docopt(__doc__, version=version)
    files = args["<files>"]

    # checkout existing output
    if args["--output"]:
        if not fileio.ContinueDump(args["--output"]):
            return 1

    # read YAML-file
    if args["--input"]:
        try:
            source = args["--input"]
            key = list(filter(None, args["--key"].split("/")))
            files = fileio.YamlGetItem(source, key)
        except Exception as e:
            print(e)
            return 1

    # check arguments
    for file in files:
        if not os.path.isfile(file):
            print('"%s" does not exist' % file)
            return 1

    # submit
    pbar = tqdm.tqdm(files, disable=args["--quiet"])

    for ifile, file in enumerate(pbar):
        pbar.set_description(file)
        path, name = os.path.split(file)

        commands = []

        if len(path) > 0:
            commands += [f"cd {path}"]

        submit = ["sbatch"]
        if args["--wait"]:
            submit += ["--wait"]
        if args["--constraint"]:
            submit += ["--constraint {:s}".format(args["--constraint"])]
        submit += [name]
        commands += [" ".join(submit)]

        run(" && ".join(commands), verbose=args["--verbose"], dry_run=args["--dry-run"])
        dump(files, ifile + 1, args["--output"])
        time.sleep(float(args["--delay"]))
