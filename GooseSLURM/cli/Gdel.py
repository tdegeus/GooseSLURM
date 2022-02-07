r"""Gdel
    Stop running jobs.

Usage:
    Gdel [options]
    Gdel [options] <JobId>...

Arguments:
    ID-number(s) of the job(s) to delete. (default: all user's jobs)

Options:
    --no-truncate
        Print full columns, do not truncate based on screen width.

    --width=<N>
        Set print with.

    --colors=<NAME>
        Select color scheme from: none, dark. [default: dark]

    --sep=<NAME>
        Set column separator. [default:  ] (space)

    --debug=<FILE>
        Debug. Output `squeue -o "%all"` provided from file.

    -h, --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""
import os
import pwd
import re
import subprocess
import sys

import click
import docopt

from .. import rich
from .. import squeue
from .. import table
from .. import version


def main():

    # -- parse command line arguments --

    # parse command-line options
    args = docopt.docopt(__doc__, version=version)

    # change keys to simplify implementation:
    # - remove leading "-" and "--" from options
    args = {re.sub(r"([\-]{1,2})(.*)", r"\2", key): args[key] for key in args}
    # - change "-" to "_" to facilitate direct use in print format
    args = {key.replace("-", "_"): args[key] for key in args}
    # - remove "<...>"
    args = {re.sub(r"(<)(.*)(>)", r"\2", key): args[key] for key in args}

    # -- field-names and print settings --

    # conversion map: default field-names -> custom field-names
    alias = {
        "JOBID": "JobID",
        "USER": "User",
        "ACCOUNT": "Account",
        "NAME": "Name",
        "START_TIME": "Tstart",
        "TIME_LEFT": "Tleft",
        "NODES": "#node",
        "CPUS": "#CPU",
        "CPUS_R": "#CPU(R)",
        "CPUS_PD": "#CPU(PD)",
        "MIN_MEMORY": "MEM",
        "ST": "ST",
        "NODELIST(REASON)": "Host",
        "PARTITION": "Partition",
        "DEPENDENCY": "Dependency",
        "WORK_DIR": "WorkDir",
    }

    # conversion map: custom field-names -> default field-names
    aliasInv = {alias[key].upper(): key for key in alias}

    # rename command line options -> default field-names
    # - add key-names
    aliasInv["STATUS"] = "ST"
    # - apply conversion
    for key in [key for key in args]:
        if key.upper() in aliasInv:
            args[aliasInv[key.upper()]] = args.pop(key)

    # print settings of all columns
    # - "width"   : minimum width, adapted to print width (min_width <= width <= real_width)
    # - "align"   : alignment of the columns (except the header)
    # - "priority": priority of column expansing, columns marked "True" are expanded first
    columns = [
        {"key": "JOBID", "width": 7, "align": ">", "priority": True},
        {"key": "USER", "width": 7, "align": "<", "priority": True},
        {"key": "ACCOUNT", "width": 7, "align": "<", "priority": True},
        {"key": "NAME", "width": 11, "align": "<", "priority": False},
        {"key": "START_TIME", "width": 6, "align": ">", "priority": True},
        {"key": "TIME_LEFT", "width": 5, "align": ">", "priority": True},
        {"key": "NODES", "width": 5, "align": ">", "priority": True},
        {"key": "CPUS", "width": 4, "align": ">", "priority": True},
        {"key": "MIN_MEMORY", "width": 3, "align": ">", "priority": True},
        {"key": "ST", "width": 2, "align": "<", "priority": True},
        {"key": "PARTITION", "width": 9, "align": "<", "priority": False},
        {"key": "NODELIST(REASON)", "width": 5, "align": "<", "priority": False},
        {"key": "DEPENDENCY", "width": 5, "align": "<", "priority": False},
        {"key": "WORK_DIR", "width": 7, "align": "<", "priority": False},
    ]

    # header
    header = {
        column["key"]: rich.String(alias[column["key"]], align=column["align"])
        for column in columns
    }

    # select color theme
    theme = squeue.colors(args["colors"].lower())

    # -- load the output of "squeue" --

    if not args["debug"]:

        lines = squeue.read_interpret(theme=theme)

    else:

        lines = squeue.read_interpret(
            data=open(args["debug"]).read(),
            now=os.path.getctime(args["debug"]),
            theme=theme,
        )

    # -- get/check running jobs --

    # get user-name
    user = pwd.getpwuid(os.getuid())[0]

    # filter to current user
    lines = [line for line in lines if re.match(user, str(line["USER"]))]

    # filter to running/queued jobs (other jobs cannot be cancelled)
    lines = [line for line in lines if str(line["ST"]) in ["R", "PD"]]

    # list with fields on which filters are applied
    filters = ["USER", "ST"]

    # filter to input list of job-ids
    if args["JOBID"]:
        # - convert to set
        jobs = set(args["JOBID"])
        # - filter running jobs
        lines = [line for line in lines if str(line["JOBID"]) in jobs]
        # - set selection-color
        filters += ["JOBID"]

    # set selection-color
    for key in filters:
        for line in lines:
            line[key].color = theme["selection"]

    # no jobs -> quit
    if len(lines) == 0:
        sys.exit(0)

    # -- prompt confirmation, cancel jobs --

    # print header
    print("Delete jobs : ")

    # print selected jobs
    table.print_columns(lines, columns, header, args["no_truncate"], args["sep"], args["width"])

    # prompt response
    if not click.confirm("Proceed?"):
        sys.exit(1)

    # construct command
    cmd = "scancel " + " ".join([str(line["JOBID"]) for line in lines])

    # run/print command
    if not args["debug"]:
        print(subprocess.check_output(cmd, shell=True).decode("utf-8"), end="")
    else:
        print(cmd)
