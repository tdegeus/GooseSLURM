r"""Gsub
    Submit job-scripts from their directory.

Usage:
    Gsub [options] --input=arg
    Gsub [options] <files>...

Arguments:
    Job-scripts.

Options:
    -c, --constrain=arg
        Add *sbatch* command-line option ``constrain``.

    -t, --time=arg
        Add *sbatch* command-line option ``time``.

    -a, --account=arg
        Add *sbatch* command-line option ``account``.

    -i, --input=arg
        Submit job-scripts stored in YAML-file.

    -k, --key=arg
        Path in the input YAML-file, separated by "/". [default: /]

    -o, --output=arg
        Output submitted/pending job-scripts to YAML-file (updated after each submit).

    -w, --wait=arg
        Seconds to wait between submitting jobs. [default: 0.1]

    -s, --serial
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


def run(cmd, verbose=False, dry_run=False):

    if dry_run:
        print(cmd)
        return None

    ret = subprocess.check_output(cmd, shell=True).decode("utf-8")

    if verbose:
        print(cmd)
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

    parser.add_argument("-c", "--constrain", type=str)
    parser.add_argument("-t", "--time", type=str)
    parser.add_argument("-a", "--account", type=str)
    parser.add_argument("-i", "--input", type=str)
    parser.add_argument("-k", "--key", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-w", "--wait", type=float, default=0.1)
    parser.add_argument("-s", "--serial", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("files", nargs="*", type=str)
    args = parser.parse_args()

    # checkout existing output
    if args.output:
        if not fileio.ContinueDump(args.output):
            return 1

    # interpret YAML-file
    if args.input:
        assert os.path.isfile(os.path.realpath(args.input))
        assert len(args.files) == 0
        key = list(filter(None, args["--key"].split("/")))
        args.files = fileio.YamlGetItem(args.input, key)

    assert all([os.path.isfile(os.path.realpath(file)) for file in args.files])

    # construct command
    sbatch = ["sbatch"]
    for key, opt in zip(["constrain", "time", "account"], [args.constrain, args.time, args.account]):
        if opt:
            sbatch += [f"--{key} {opt}"]

    # submit
    pbar = tqdm.tqdm(args.files, disable=args["--quiet"])

    for ifile, file in enumerate(pbar):
        pbar.set_description(file)
        path, name = os.path.split(file)

        if len(path) > 0:
            cmd = f"cd {path}; " + " ".join(sbatch + [name])
        else:
            cmd = " ".join(sbatch + [name])

        ret = run(cmd, verbose=args.verbose, dry_run=args.dry_run)
        dump(args.files, ifile + 1, args.output)

        if args.serial:
            jobid = ret.split("Submitted batch job ")[1]
            time.sleep(20)
            while True:
                start = time.time()
                status = run("squeue -j {0:s}".format(jobid)).split("\n")
                end = time.time()
                if len(status) == 1:
                    break
                if len(status) == 2:
                    if len(status[1]) == 0:
                        break
                if end - start < 20:
                    time.sleep(20 - (end - start))

        time.sleep(float(args.wait))


def main():

    try:
        run()
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":

    main()
