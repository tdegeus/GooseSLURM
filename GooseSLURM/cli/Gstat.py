"""Gstat
    Summarize the status of the jobs (wrapper around "squeue") using (some of) the following fields:

        +--------------+------------------------------------------------+
        | Header       | Description                                    |
        +--------------+------------------------------------------------+
        | "JobID"      | Job-id                                         |
        | "User"       | Username                                       |
        | "Account"    | Account name                                   |
        | "Name"       | Job name                                       |
        | "Tstart"     | Time as which the job will start / has started |
        | "Tleft"      | Maximum duration left                          |
        | "#node"      | Number of nodes claimed                        |
        | "#CPU"       | Number of CPUs claimed                         |
        | "MEM"        | Memory claimed                                 |
        | "ST"         | Status                                         |
        | "Partition"  | Partition                                      |
        | "Host"       | Hostname                                       |
        | "Dependency" | Dependency / dependencies                      |
        | "WorkDir"    | Working directory                              |
        +--------------+------------------------------------------------+

Usage:
    Gstat [options]
    Gstat [options] [--jobid=N...] [--host=N...] [--user=N...] [--name=N...] [--workdir=N...] [--account=N...] [--partition=N...] [--sort=N...] [--output=N...] [--extra=N...]

Options:
    -U
        Limit output to the current user.

    -u, --user=<NAME>
        Limit output to user(s) (may be a regex).

    -j, --jobid=<NAME>
        Limit output to job-id(s) (may be a regex).

    -h, --host=<NAME>
        Limit output to host(s) (may be a regex).

    -a, --account=<NAME>
        Limit output to account(s) (may be a regex).

    -n, --name=<NAME>
        Limit output to job-name(s) (may be a regex).

    -w, --workdir=<NAME>
        Limit output to job-name(s) (may be a regex).
        Consider using ``--abspath`` or ``--relpath``.

    --status=<NAME>
        Limit output to status (may be a regex).

    -p, --partition=<NAME>
        Limit output to partition(s) (may be a regex).

    -s, --sort=<NAME>
        Sort by field (selected by the header name).

    -r, --reverse
        Reverse sort.

    -o, --output=<NAME>
        Select output columns (see description).

    -e, --extra=<NAME>
        Add columns (see description).

    --full-name
        Show full user names.

    -S, --summary
        Print only summary.

    --no-header
        Suppress header.

    --no-truncate
        Print full columns, do not truncate based on screen width.

    --width=<N>
        Set line-width (otherwise equal to the terminal width).

    --colors=<NAME>
        Select color scheme from: none, dark. [default: dark]

    -l, --list
        Print selected column as list.

    -J, --joblist
        Print selected job-id(s) as list. Sort for ``Gstat -o jobid -l``.

    --abspath
        Print directories as absolute directories (default: automatic, based on distance).

    --relpath
        Print directories as relative directories (default: automatic, based on distance).

    --sep=<NAME>
        Set column separator. [default:  ] (space) # argparse

    --long
        Print full information (each column is printed as a line).

    --debug=<FILE>
        Debug: read ``squeue -o "%all"`` from file.

    --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""
import os
import pwd
import re
import sys

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

    # -- field-names and print settings --

    # handle 'alias' options
    if args["U"]:
        args["user"] += [pwd.getpwuid(os.getuid())[0]]

    if args["joblist"]:
        args["output"] = ["JOBID"]
        args["list"] = True

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
        {"key": "JOBID", "width": 7, "align": ">", "priority": True, "default": True},
        {"key": "USER", "width": 7, "align": "<", "priority": True, "default": True},
        {"key": "ACCOUNT", "width": 7, "align": "<", "priority": True, "default": True},
        {"key": "NAME", "width": 11, "align": "<", "priority": False, "default": True},
        {"key": "START_TIME", "width": 6, "align": ">", "priority": True, "default": True},
        {"key": "TIME_LEFT", "width": 5, "align": ">", "priority": True, "default": True},
        {"key": "NODES", "width": 5, "align": ">", "priority": True, "default": True},
        {"key": "CPUS", "width": 4, "align": ">", "priority": True, "default": True},
        {"key": "MIN_MEMORY", "width": 3, "align": ">", "priority": True, "default": True},
        {"key": "ST", "width": 2, "align": "<", "priority": True, "default": True},
        {"key": "PARTITION", "width": 9, "align": "<", "priority": False, "default": True},
        {"key": "NODELIST(REASON)", "width": 5, "align": "<", "priority": False, "default": True},
        {"key": "DEPENDENCY", "width": 5, "align": "<", "priority": False, "default": False},
        {"key": "WORK_DIR", "width": 7, "align": "<", "priority": False, "default": False},
    ]

    # header
    header = {
        column["key"]: rich.String(alias[column["key"]], align=column["align"])
        for column in columns
    }

    # print settings for the summary
    columns_summary = [
        {"key": "USER", "width": 7, "align": "<", "priority": True},
        {"key": "ACCOUNT", "width": 7, "align": "<", "priority": False},
        {"key": "CPUS", "width": 4, "align": ">", "priority": True},
        {"key": "CPUS_R", "width": 6, "align": ">", "priority": True},
        {"key": "CPUS_PD", "width": 6, "align": ">", "priority": True},
        {"key": "PARTITION", "width": 9, "align": "<", "priority": False},
    ]

    # header
    header_summary = {
        column["key"]: rich.String(alias[column["key"]], align=column["align"])
        for column in columns_summary
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

    # -- convert paths ---

    if args["abspath"]:
        for line in lines:
            line["WORK_DIR"].data = os.path.abspath(line["WORK_DIR"].data)
    elif args["relpath"]:
        for line in lines:
            line["WORK_DIR"].data = os.path.relpath(line["WORK_DIR"].data)
    else:
        for line in lines:
            if len(os.path.relpath(line["WORK_DIR"].data).split("../")) < 3:
                line["WORK_DIR"].data = os.path.relpath(line["WORK_DIR"].data)

    # -- limit based on command-line options --

    for key in [
        "USER",
        "ACCOUNT",
        "NAME",
        "JOBID",
        "ST",
        "NODELIST(REASON)",
        "PARTITION",
        "WORK_DIR",
    ]:

        if args[key]:

            # limit data
            lines = [
                line
                for line in lines
                if sum(1 if re.match(n, str(line[key])) else 0 for n in args[key])
            ]

            # color-highlight selected columns
            # - apply to all remaining lines
            for line in lines:
                line[key].color = theme["selection"]
            # - apply to the header
            header[key].color = theme["selection"]

    # -- sort --

    # default sort
    lines.sort(key=lambda line: line["START_TIME"], reverse=not args["reverse"])

    # optional: sort by key(s)
    if args["sort"]:
        for key in args["sort"]:
            lines.sort(key=lambda line: line[aliasInv[key.upper()]], reverse=args["reverse"])

    # -- select columns --

    if args["extra"]:
        keys = [aliasInv[key.upper()] for key in args["extra"]]
        extra = [column for column in columns if column["key"] in keys]
    else:
        extra = []

    if args["output"]:
        keys = [aliasInv[key.upper()] for key in args["output"]]
        columns = [column for column in columns if column["key"] in keys]
    else:
        columns = [column for column in columns if column["default"]]

    columns += extra

    # -- print --

    if not args["summary"]:

        # optional: print all fields and quit
        if args["long"]:
            table.print_long(lines)
            return 0

        # optional: print as list and quit
        elif args["list"]:
            if len(columns) > 1:
                print("Only one field can be selected")
                sys.exit(1)

            table.print_list(lines, columns[0]["key"], args["sep"])
            return 0

        # default: print columns
        else:
            table.print_columns(
                lines,
                columns,
                header,
                args["no_truncate"],
                args["sep"],
                int(args["width"]) if args["width"] else args["width"],  # remove int for argparse
                not args["no_header"],
            )
            return 0

    # -- summarize information --

    # get names of the different users
    users = sorted({str(line["USER"]) for line in lines})

    # start a new list of "user information", summed on the relevant users
    users = [{"USER": rich.String(key)} for key in users]

    # loop over users
    for user in users:

        # - isolate jobs for this user
        N = [line for line in lines if str(line["USER"]) == str(user["USER"])]

        # - get (a list of) partition(s)/account(s)
        user["PARTITION"] = rich.String(",".join(list({str(line["PARTITION"]) for line in N})))
        user["ACCOUNT"] = rich.String(",".join(list({str(line["ACCOUNT"]) for line in N})))

        # - count used CPU (per category)
        user["CPUS"] = rich.Integer(sum(int(line["CPUS"]) for line in N))
        user["CPUS_R"] = rich.Integer(sum(int(line["CPUS_R"]) for line in N))
        user["CPUS_PD"] = rich.Integer(sum(int(line["CPUS_PD"]) for line in N))

        # - remove zeros from output for more intuitive output
        for key in ["CPUS_R", "CPUS_PD"]:
            if int(user[key]) == 0:
                user[key] = rich.Integer("-")

    # rename field
    lines = users

    # -- sort --

    # default sort
    lines.sort(key=lambda line: line["USER"], reverse=args["reverse"])

    # optional: sort by key(s)
    if args["sort"]:

        # get available keys in the setting with fewer columns
        keys = [alias[column["key"]].upper() for column in columns_summary]

        # filter sort keys that are not available in this mode
        args["sort"] = [key for key in args["sort"] if key.upper() in keys]

        # apply sort
        for key in args["sort"]:
            lines.sort(key=lambda line: line[aliasInv[key.upper()]], reverse=args["reverse"])

    # -- print --

    table.print_columns(
        lines,
        columns_summary,
        header_summary,
        args["no_truncate"],
        args["sep"],
        args["width"],
        not args["no_header"],
    )
