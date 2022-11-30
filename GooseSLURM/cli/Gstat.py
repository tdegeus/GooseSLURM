"""Gstat
    Summarize the status of the jobs (wrapper around "squeue") using (some of) the following fields:

        +--------------+------------------------------------------------+
        | Header       | Description                                    |
        +==============+================================================+
        | "JobID"      | Job-id                                         |
        +--------------+------------------------------------------------+
        | "User"       | Username                                       |
        +--------------+------------------------------------------------+
        | "Account"    | Account name                                   |
        +--------------+------------------------------------------------+
        | "Name"       | Job name                                       |
        +--------------+------------------------------------------------+
        | "Tstart"     | Time as which the job will start / has started |
        +--------------+------------------------------------------------+
        | "Tleft"      | Maximum duration left                          |
        +--------------+------------------------------------------------+
        | "#node"      | Number of nodes claimed                        |
        +--------------+------------------------------------------------+
        | "#CPU"       | Number of CPUs claimed                         |
        +--------------+------------------------------------------------+
        | "MEM"        | Memory claimed                                 |
        +--------------+------------------------------------------------+
        | "ST"         | Status                                         |
        +--------------+------------------------------------------------+
        | "Partition"  | Partition                                      |
        +--------------+------------------------------------------------+
        | "Host"       | Hostname                                       |
        +--------------+------------------------------------------------+
        | "Dependency" | Dependency / dependencies                      |
        +--------------+------------------------------------------------+
        | "WorkDir"    | Working directory                              |
        +--------------+------------------------------------------------+

Usage:
    Gstat [options]
    Gstat [options] <JobId>...

Options:
    -U
        Limit output to the current user.

    -u, --user=<NAME>
        Limit output to user(s).
        Option may be repeated. Search by regex.

    -j, --jobid=<NAME>
        Limit output to job-id(s).
        Option may be repeated. Search by regex.

    --root=<NAME>
        Filter jobs whose workdir has this root.

    --host=<NAME>
        Limit output to host(s).
        Option may be repeated. Search by regex.

    -a, --account=<NAME>
        Limit output to account(s).
        Option may be repeated. Search by regex.

    -n, --name=<NAME>
        Limit output to job-name(s).
        Option may be repeated. Search by regex.

    -w, --workdir=<NAME>
        Limit output to job-name(s).
        Option may be repeated. Search by regex.

    --status=<NAME>
        Limit output to status.
        Option may be repeated. Search by regex.

    -p, --partition=<NAME>
        Limit output to partition(s).
        Option may be repeated. Search by regex.

    -s, --sort=<NAME>
        Sort by field.
        Option may be repeated. See description for header names.

    -r, --reverse
        Reverse sort.

    -o, --output=<NAME>
        Select output columns.
        Option may be repeated. See description for header names.

    -e, --extra=<NAME>
        Add columns.
        Option may be repeated. See description for header names.

    --full-name
        Show full user names.

    -S, --summary
        Print only summary.

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

    -J, --joblist
        Print selected job-id(s) as list. Sort for ``Gstat -o jobid -l``.

    --abspath
        Print directories as absolute directories (default: automatic, based on distance).

    --relpath
        Print directories as relative directories (default: automatic, based on distance).

    --sep=<NAME>
        Set column separator. [default: " "]

    --long
        Print full information (each column is printed as a line).

    --debug=<FILE>
        Debug: read ``squeue -o "%all"`` from file.

    -d, --print-dependency
        Print the selected jobs as ``-d <jobid> -d <jobid> ...``.
        Use to for example ``Gsub *slurm `Gstat -d -U --partition "serial"```.

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

import numpy as np

from .. import rich
from .. import squeue
from .. import table
from .. import version


class Gstat:
    def __init__(self):
        pass

    def parse_cli_args(self, cli_args: list[str] = None):
        """
        Parse command-line arguments.
        Stores the arguments as ``self.args``

        :param cli_args: Specify command-line arguments. Default: ``sys.argv[1:]``.
        """

        class Parser(argparse.ArgumentParser):
            def print_help(self):
                print(__doc__)

        parser = Parser()
        parser.add_argument("-U", action="store_true")
        parser.add_argument("-u", "--user", type=str, action="append", default=[])
        parser.add_argument("-j", "--jobid", type=str, action="append", default=[])
        parser.add_argument("--host", type=str, action="append")
        parser.add_argument("--root", type=str)
        parser.add_argument("-a", "--account", type=str, action="append")
        parser.add_argument("-n", "--name", type=str, action="append")
        parser.add_argument("-w", "--workdir", type=str, action="append")
        parser.add_argument("--status", type=str, action="append")
        parser.add_argument("-p", "--partition", type=str, action="append")
        parser.add_argument("-s", "--sort", type=str, action="append")
        parser.add_argument("-r", "--reverse", action="store_true")
        parser.add_argument("-o", "--output", type=str, action="append")
        parser.add_argument("-e", "--extra", type=str, action="append")
        parser.add_argument("--full-name", action="store_true")
        parser.add_argument("-S", "--summary", action="store_true")
        parser.add_argument("--no-header", action="store_true")
        parser.add_argument("--no-truncate", action="store_true")
        parser.add_argument("--width", type=int)
        parser.add_argument("--colors", type=str, default="dark")
        parser.add_argument("-l", "--list", action="store_true")
        parser.add_argument("-J", "--joblist", action="store_true")
        parser.add_argument("--abspath", action="store_true")
        parser.add_argument("--relpath", action="store_true")
        parser.add_argument("--sep", type=str, default=" ")
        parser.add_argument("--long", action="store_true")
        parser.add_argument("--debug", type=str)
        parser.add_argument("-d", "--print-dependency", action="store_true")
        parser.add_argument("--version", action="version", version=version)
        parser.add_argument("jobs", type=int, nargs="*")

        if cli_args is None:
            args = vars(parser.parse_args())
        else:
            args = vars(parser.parse_args(cli_args))

        if args["U"]:
            args["user"] += [pwd.getpwuid(os.getuid())[0]]

        if args["joblist"]:
            args["output"] = ["JOBID"]
            args["list"] = True

        args["jobid"] += [f"^{i:d}$" for i in args["jobs"]]

        if args["root"]:
            if args["extra"] is None:
                args["extra"] = ["WorkDir"]
            elif "WorkDir" not in args["extra"]:
                args["extra"] += ["WorkDir"]

        # store for later use
        self.args = args

    def read(self):
        """
        Read from queuing system.
        Stores data on ``self.lines``
        Store print info as``self.columns``, ``self.header``, ``self.alias``, ``self.aliasInv``.
        """

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
        for key in [key for key in self.args]:
            if key.upper() in aliasInv:
                self.args[aliasInv[key.upper()]] = self.args.pop(key)

        # print settings of all columns
        # - "width"   : minimum width, adapted to print width (min_width <= width <= real_width)
        # - "align"   : alignment of the columns (except the header)
        # - "priority": priority of column expansing, columns marked "True" are expanded first
        prio = {"priority": True, "default": True}
        noprio = {"priority": False, "default": True}
        nodefault = {"priority": True, "default": False}
        columns = [
            {"key": "JOBID", "width": 7, "align": ">", **prio},
            {"key": "USER", "width": 7, "align": "<", **prio},
            {"key": "ACCOUNT", "width": 7, "align": "<", **prio},
            {"key": "NAME", "width": 11, "align": "<", **noprio},
            {"key": "START_TIME", "width": 6, "align": ">", **prio},
            {"key": "TIME_LEFT", "width": 5, "align": ">", **prio},
            {"key": "NODES", "width": 5, "align": ">", **prio},
            {"key": "CPUS", "width": 4, "align": ">", **prio},
            {"key": "MIN_MEMORY", "width": 3, "align": ">", **prio},
            {"key": "ST", "width": 2, "align": "<", **prio},
            {"key": "PARTITION", "width": 9, "align": "<", **noprio},
            {"key": "NODELIST(REASON)", "width": 5, "align": "<", **noprio},
            {"key": "DEPENDENCY", "width": 5, "align": "<", **nodefault},
            {"key": "WORK_DIR", "width": 7, "align": "<", **nodefault},
        ]

        # header
        header = {
            column["key"]: rich.String(alias[column["key"]], align=column["align"])
            for column in columns
        }

        if self.args["root"]:
            header["WORK_DIR"] = rich.String(header["WORK_DIR"].data + " " + self.args["root"])

        # select color theme
        theme = squeue.colors(self.args["colors"].lower())

        # -- load the output of "squeue" --

        if not self.args["debug"]:

            lines = squeue.read_interpret(theme=theme)

        else:

            lines = squeue.read_interpret(
                data=open(self.args["debug"]).read(),
                now=os.path.getctime(self.args["debug"]),
                theme=theme,
            )

        # -- convert paths ---

        if self.args["root"]:
            root = self.args["root"]
            lines = [
                i for i in lines if not os.path.relpath(i["WORK_DIR"].data, root).startswith("..")
            ]
            for line in lines:
                line["WORK_DIR"].data = os.path.relpath(line["WORK_DIR"].data, root)
        elif self.args["abspath"]:
            for line in lines:
                line["WORK_DIR"].data = os.path.abspath(line["WORK_DIR"].data)
        elif self.args["relpath"]:
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

            if not self.args[key]:
                continue

            # limit data
            lines = [
                line
                for line in lines
                if sum(1 if re.match(n, str(line[key])) else 0 for n in self.args[key])
            ]

            # color-highlight selected columns
            # - apply to all remaining lines
            for line in lines:
                line[key].color = theme["selection"]
            # - apply to the header
            header[key].color = theme["selection"]

        if self.args["root"]:
            key = "WORK_DIR"

            for line in lines:
                line[key].color = theme["selection"]

            header[key].color = theme["selection"]

        # -- sort --

        if self.args["sort"]:
            sortkeys = [aliasInv[key.upper()] for key in self.args["sort"]]
            reversed = False
        else:
            sortkeys = ["JOBID", "PARTITION"]
            reversed = False

        if self.args["reverse"]:
            reversed = not reversed

        idx = np.lexsort([[i[key] for i in lines] for key in sortkeys])
        if reversed:
            idx = idx[::-1]
        lines = [lines[i] for i in idx]

        # -- select columns --

        if self.args["extra"]:
            keys = [aliasInv[key.upper()] for key in self.args["extra"]]
            extra = [column for column in columns if column["key"] in keys]
        else:
            extra = []

        if self.args["output"]:
            keys = [aliasInv[key.upper()] for key in self.args["output"]]
            columns = [column for column in columns if column["key"] in keys]
        else:
            columns = [column for column in columns if column["default"]]
            columns += extra

        # store for later use
        self.lines = lines
        self.columns = columns
        self.header = header
        self.alias = alias
        self.aliasInv = aliasInv

    def print_all(self):
        """
        Normal print
        """

        # print all fields and quit
        if self.args["long"]:

            table.print_long(self.lines)
            return

        # print as list and quit
        if self.args["list"]:

            if len(self.columns) > 1:
                raise OSError("Error: Only one field can be selected")

            table.print_list(self.lines, self.columns[0]["key"], self.args["sep"])

        # print columns
        table.print_columns(
            self.lines,
            self.columns,
            self.header,
            self.args["no_truncate"],
            self.args["sep"],
            self.args["width"],
            not self.args["no_header"],
        )

    def print_summary(self):
        """
        Print summary.
        """

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
            column["key"]: rich.String(self.alias[column["key"]], align=column["align"])
            for column in columns_summary
        }

        # -- summarize information --

        # get names of the different users
        users = sorted({str(line["USER"]) for line in self.lines})

        # start a new list of "user information", summed on the relevant users
        users = [{"USER": rich.String(key)} for key in users]

        # loop over users
        for user in users:

            # - isolate jobs for this user
            N = [line for line in self.lines if str(line["USER"]) == str(user["USER"])]

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
        lines.sort(key=lambda line: line["USER"], reverse=self.args["reverse"])

        # optional: sort by key(s)
        if self.args["sort"]:

            # get available keys in the setting with fewer columns
            keys = [self.alias[column["key"]].upper() for column in columns_summary]

            # filter sort keys that are not available in this mode
            self.args["sort"] = [key for key in self.args["sort"] if key.upper() in keys]

            # apply sort
            for key in self.args["sort"]:
                lines.sort(
                    key=lambda line: line[self.aliasInv[key.upper()]], reverse=self.args["reverse"]
                )

        # -- print --

        table.print_columns(
            lines,
            columns_summary,
            header_summary,
            self.args["no_truncate"],
            self.args["sep"],
            self.args["width"],
            not self.args["no_header"],
        )

    def print(self):
        """
        Print.
        """

        if self.args["print_dependency"]:
            if len(self.lines) > 0:
                print("-d " + " -d ".join([str(line["JOBID"]) for line in self.lines]))
        elif not self.args["summary"]:
            self.print_all()
        else:
            self.print_summary()


def main():
    try:
        p = Gstat()
        p.parse_cli_args()
        p.read()
        p.print()
    except Exception as e:
        print(e)
        return 1
