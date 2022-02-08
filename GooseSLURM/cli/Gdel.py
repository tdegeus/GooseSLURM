r"""Gdel
    Stop running jobs.

Usage:
    Gdel [options]
    Gdel [options] <JobId>...

Arguments:
    ID-number(s) of the job(s) to delete. (default: all user's jobs)

Options:

    ...
        Any option for ``Gstat``.

    -h, --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""
import subprocess
import sys

import click

from . import Gstat


def main():

    cli_args = sys.argv[1:]
    data = Gstat.cli(cli_args, parse_only=True)

    if len(data.args["jobs"]) == 0:
        cli_args += ["-U", "--status", "R", "--status", "PD"]

    data = Gstat.cli(cli_args, parse_only=True)

    if len(data.jobs) == 0:
        print("Nothing to do")
        return 0

    data = Gstat.cli(cli_args, parse_only=False)

    if not click.confirm("Delete above listed jobs?"):
        return 1

    cmd = "scancel " + " ".join(data.jobs)

    if not data.args["debug"]:
        print(subprocess.check_output(cmd, shell=True).decode("utf-8"), end="")
    else:
        print(cmd)
