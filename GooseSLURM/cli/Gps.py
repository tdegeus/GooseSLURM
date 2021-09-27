"""Gps
    List memory usage per process.

Usage:
    Gps [options]
    Gps [options] [--user=N...] [--pid=N...] [--command=N...] [--sort=N...] [--output=N...]

Options:
    -U
        Limit processes to the current user.

    -u, --user=<NAME>
        Limit processes to user(s)    (may be a regex).

    -p, --pid=<NAME>
        Limit processes to process-id (may be a regex).

    -c, --command=<NAME>
        Limit processes to command    (may be a regex).

    -s, --sort=<NAME>
        Sort by field (selected by the header name).

    -r, --reverse
        Reverse sort.

    --output=<NAME>
        Select output columns (selected by the header name).

    --no-header
        Suppress header.

    --no-truncate
        Print full columns, do not truncate based on screen width.

    --width=<N>
        Set print with.

    --colors=<NAME>
        Select color scheme from: none, dark. [default: dark]

    --list
        Print selected column as list.

    --sep=<NAME>
        Set column separator. [default:  ] (space)

    --long
        Print full information (each column is printed as a line).

    --debug=<FILE>
        Debug. Output ``squeue -o "%all"`` provided from file.

    -h, --help
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

from .. import version
from .. import ps
from .. import rich
from .. import table


def main():

    # -- parse command line arguments --

    # parse command-line options
    args = docopt.docopt(__doc__, version=version)

    # change keys to simplify implementation:
    # - remove leading "-" and "--" from options
    args = {re.sub(r"([\-]{1,2})(.*)", r"\2", key): args[key] for key in args}
    # - change "-" to "_" to facilitate direct use in print format
    args = {key.replace("-", "_"): args[key] for key in args}

    # -------------------------------- field-names and print settings --------

    # handle 'alias' options
    if args["U"]:
        args["user"] += [pwd.getpwuid(os.getuid())[0]]

    # conversion map: default field-names -> custom field-names
    alias = {
        "USER": "USER",
        "PID": "PID",
        "RSS": "MEM",
        "%CPU": "%CPU",
        "COMMAND": "COMMAND",
    }

    # conversion map: custom field-names -> default field-names
    aliasInv = {alias[key].upper(): key for key in alias}

    # rename command line options -> default field-names
    for key in [key for key in args]:
        if key.upper() in aliasInv:
            args[aliasInv[key.upper()]] = args.pop(key)

    # print settings of all columns
    # - "width"   : minimum width, adapted to print width (min_width <= width <= real_width)
    # - "align"   : alignment of the columns (except the header)
    # - "priority": priority of column expansing, columns marked "True" are expanded first
    columns = [
        {"key": "PID", "width": 3, "align": ">", "priority": True},
        {"key": "USER", "width": 7, "align": "<", "priority": True},
        {"key": "RSS", "width": 4, "align": ">", "priority": True},
        {"key": "%CPU", "width": 4, "align": ">", "priority": True},
        {"key": "COMMAND", "width": 10, "align": "<", "priority": True},
    ]

    # header
    header = {
        column["key"]: rich.String(alias[column["key"]], align=column["align"])
        for column in columns
    }

    # select color theme
    theme = ps.colors(args["colors"].lower())

    # -- load the output of "ps" --

    if not args["debug"]:

        lines = ps.read_interpret(theme=theme)

    else:

        lines = ps.read_interpret(
            data=open(args["debug"]).read(),
            theme=theme,
        )

    # ----------------------------- limit based on command-line options ------

    for key in ["USER", "PID", "COMMAND"]:

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
    lines.sort(key=lambda line: line["RSS"], reverse=False)

    # optional: sort by key(s)
    if args["sort"]:

        for key in args["sort"]:

            lines.sort(
                key=lambda line: line[aliasInv[key.upper()]], reverse=args["reverse"]
            )

    # -- select columns --

    if args["output"]:

        keys = [aliasInv[key.upper()] for key in args["output"]]

        columns = [column for column in columns if column["key"] in keys]

    # -- print --

    if True:

        # optional: print all fields and quit
        if args["long"]:

            table.print_long(lines)

            sys.exit(0)

        # optional: print as list and quit
        elif args["list"]:

            # - only one field can be selected
            if len(columns) > 1:
                print("Only one field can be selected")
                sys.exit(1)

            # - print and quit
            table.print_list(lines, columns[0]["key"], args["sep"])

            sys.exit(0)

        # default: print columns
        else:

            table.print_columns(
                lines,
                columns,
                header,
                args["no_truncate"],
                args["sep"],
                args["width"],
                not args["no_header"],
            )

            sys.exit(0)
