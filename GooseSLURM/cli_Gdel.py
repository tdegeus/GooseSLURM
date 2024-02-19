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

from .cli_Gstat import Gstat


def main():
    cli_args = sys.argv[1:]
    gstat = Gstat()
    gstat.parse_cli_args(cli_args)

    if len(gstat.args["jobs"]) == 0:
        if len(gstat.args["user"]) == 0:
            cli_args += ["-U"]
        if gstat.args["status"] is None:
            cli_args += ["--status", "R", "--status", "PD"]
        gstat.parse_cli_args(cli_args)

    gstat.read()

    if len(gstat.lines) == 0:
        print("Nothing to do")
        return 0

    gstat.print()

    if not click.confirm("Delete above listed jobs?"):
        return 1

    cmd = ["scancel"] + [str(line["JOBID"]) for line in gstat.lines]

    if not gstat.args["debug"]:
        print(subprocess.run(cmd, capture_output=True, text=True).stdout, end="")
    else:
        print(cmd)
