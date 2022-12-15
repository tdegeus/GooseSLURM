"""Gps
    List memory usage per process.

        +--------------+------------------------------------------------+
        | Header       | Description                                    |
        +==============+================================================+
        | "PID"        | Process-id                                     |
        +--------------+------------------------------------------------+
        | "USER"       | Username                                       |
        +--------------+------------------------------------------------+
        | "MEM"        | Memory used                                    |
        +--------------+------------------------------------------------+
        | "%CPU"       | Fraction of CPU capacity used                  |
        +--------------+------------------------------------------------+
        | "TIME"       | Duration of the command                        |
        +--------------+------------------------------------------------+
        | "COMMAND"    | Command                                        |
        +--------------+------------------------------------------------+

    .. tip::

        A nice use is to kill a command filtered on its name::

            kill `Gps -9 -c ".*mycommand.*"`

        Of course you should probably verify the selected pid(s) before killing them.

Usage:
    Gps [options]

Options:
    -U
        Limit processes to the current user.

    -u, --user=<NAME>
        Limit processes to user(s).
        Option may be repeated. Search by regex.

    -p, --pid=<NAME>
        Limit processes to process-id.
        Option may be repeated. Search by regex.

    -c, --command=<NAME>
        Limit processes to command.
        Option may be repeated. Search by regex.

    --include-me
        Include the current process.

    -s, --sort=<NAME>
        Sort by field (selected by the header name).

    -r, --reverse
        Reverse sort.

    -o, --output=<NAME>
        Select output columns.
        Option may be repeated. See description for header names.

    --no-header
        Suppress header.

    --no-truncate
        Print full columns, do not truncate based on terminal width.

    --width=<N>
        Set line-width (otherwise taken as terminal width).

    --colors=<NAME>
        Select color scheme from: "none", "dark". [default: "dark"]

    -l, --list
        Print selected column as list.

    --sep=<NAME>
        Set column separator. [default: " "]

    --long
        Print full information (each column is printed as a line).

    --debug=<FILE>
        Debug: read ``squeue -o "%all"`` from file.

    -h, --help
        Show help.

    --version
        Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
"""
import argparse
import os
import pwd
import re
import sys

from .. import ps
from .. import rich
from .. import table
from .. import version


def main():

    # -- parse command line arguments --

    class Parser(argparse.ArgumentParser):
        def print_help(self):
            print(__doc__)

    parser = Parser()
    parser.add_argument("-U", action="store_true")
    parser.add_argument("-u", "--user", type=str, action="append", default=[])
    parser.add_argument("-p", "--pid", type=str, action="append")
    parser.add_argument("-c", "--command", type=str, action="append")
    parser.add_argument("-s", "--sort", type=str, action="append")
    parser.add_argument("-r", "--reverse", action="store_true")
    parser.add_argument("-o", "--output", type=str, action="append")
    parser.add_argument("--no-header", action="store_true")
    parser.add_argument("--no-truncate", action="store_true")
    parser.add_argument("--width", type=int)
    parser.add_argument("--colors", type=str, default="dark")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("--sep", type=str, default=" ")
    parser.add_argument("--long", action="store_true")
    parser.add_argument("--include-me", action="store_true")
    parser.add_argument("-9", action="store_true")
    parser.add_argument("--debug", type=str)
    parser.add_argument("--version", action="version", version=version)
    args = vars(parser.parse_args())

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
        "TIME": "TIME",
        "COMMAND": "COMMAND",
    }

    # conversion map: custom field-names -> default field-names
    aliasInv = {alias[key].upper(): key for key in alias}
    aliasInv["CPU"] = "%CPU"

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
        {"key": "TIME", "width": 4, "align": ">", "priority": True},
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

        if not args["include_me"]:
            pid = os.getpid()
            lines = [line for line in lines if int(line["PID"].data) != pid]

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

            lines.sort(key=lambda line: line[aliasInv[key.upper()]], reverse=args["reverse"])

    # -- print PID only --

    if args["9"]:

        if len(lines) == 0:
            return

        print("-9 " + " ".join([str(line["PID"]) for line in lines]))
        return

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
