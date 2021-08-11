r"""Gsub
    Submit job-scripts from the directory of the job-script.

Usage:
    Gsub [options] --input=arg
    Gsub [options] <files>...

Arguments:
    Job-scripts.

Options:
    -c, --constraint=arg
        Add *sbatch* command-line option ``constraint``.
        If this option is repeated, submission will be for each of the constraints.

    -t, --time=arg
        Add *sbatch* command-line option ``time``.

    -a, --account=arg
        Add *sbatch* command-line option ``account``.

    -i, --input=arg
        Submit job-scripts stored in YAML-file.

    -k, --key=arg
        Path in the input YAML-file, separated by "/". [default: /]

    --status=arg
        Output submitted/pending job-scripts to YAML-file (updated after each submit).

    -d, --delay=arg
        Seconds to delay between submitting jobs. [default: 0.1]

    -w, --wait
        Serial submission: submit the next job only when the previous is finished.
        Can be useful for example on build partitions.

    --dry-run
        Print commands to screen, without executing.

    --verbose
        Verbose all commands and their output.

    -q, --quiet
        Do no show progress-bar.

    -h, --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""

import argparse
import os
import subprocess
import time
import tqdm

from .. import __version__
from .. import fileio


def cd_myexec(args, cwd, verbose=False, dry_run=False):

    if dry_run:
        print(f"cd {cwd}; " + " ".join(args))
        return None

    ret = subprocess.check_output(args, cwd=cwd, shell=True).decode("utf-8")

    if verbose:
        print(f"cd {cwd}; " + " ".join(args))
        print(ret, end="")

    return ret


def myexec(args, verbose=False, dry_run=False):

    if dry_run:
        print(" ".join(args))
        return None

    ret = subprocess.check_output(args, shell=True).decode("utf-8")

    if verbose:
        print(" ".join(args))
        print(ret, end="")

    return ret


def dump(files, ifile, outname):

    if not outname:
        return

    data = {
        "submitted": [files[i] for i in range(ifile)],
        "pending": [files[i] for i in range(ifile, len(files))]
    }

    fileio.YamlDump(outname, data)


def run():

    class Parser(argparse.ArgumentParser):
        def print_help(self):
            print(__doc__)

    parser = Parser()

    parser.add_argument("-c", "--constraint", type=str, action='append')
    parser.add_argument("-t", "--time", type=str)
    parser.add_argument("-a", "--account", type=str)
    parser.add_argument("-i", "--input", type=str)
    parser.add_argument("-k", "--key", type=str)
    parser.add_argument("--status", type=str)
    parser.add_argument("-d", "--delay", type=float, default=0.1)
    parser.add_argument("-w", "--wait", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("files", nargs="*", type=str)
    args = parser.parse_args()

    if not args.constraint:
        args.constraint = [None]

    if args.dry_run:
        args.quiet = True
        args.verbose = True

    # prompt to overwrite existing status-file
    if args.status:
        if not fileio.ContinueDump(args.status):
            return 1

    # interpret YAML-file
    if args.input:
        assert os.path.isfile(os.path.realpath(args.input))
        assert len(args.files) == 0
        key = list(filter(None, args["--key"].split("/")))
        args.files = fileio.YamlGetItem(args.input, key)

    assert len(args.files) > 0
    assert all([os.path.isfile(os.path.realpath(file)) for file in args.files])

    # construct command
    sbatch = ["sbatch"]
    for key, opt in zip(["time", "account", "wait"], [args.time, args.account, arg.wait]):
        if opt:
            sbatch += [f"--{key} {opt}"]

    # submit

    cbar = tqdm.tqdm(args.constraint, disable=args.quiet or len(args.constraint) == 1)

    for constraint in cbar:

        cbar.set_description(constraint)

        opt = []

        if constraint:
            opt += [f"--constraint {constraint}"]

        fbar = tqdm.tqdm(args.files, disable=args.quiet)

        for ifile, file in enumerate(fbar):

            fbar.set_description(file)
            path, name = os.path.split(file)
            cmd = sbatch + opt + [name]

            if len(path) > 0:
                ret = cd_myexec(cmd, path, verbose=args.verbose, dry_run=args.dry_run)
            else:
                ret = myexec(cmd, verbose=args.verbose, dry_run=args.dry_run)

            dump(args.files, ifile + 1, args.status)

            time.sleep(float(args.delay))


def main():

    # try:
    run()
    # except Exception as e:
    #     print(e)
    #     return 1


if __name__ == "__main__":

    main()
