"""Ginfo
    Summarize the status of the compute nodes (wrapper around "sinfo").

    The following scores are computed of each node:

    *   CPU% : The CPU load of the node relative to the number of jobs (``cpu_load / cpu_used``).
        Should always be ~1, anything else usually signals misuse.

    *   Mem% : the amount of used memory relative to the average memory available per job
        (``(mem_used / cpu_used) / (mem_tot / cpu_tot)``).
        Can be > 1 for (several) heavy memory consumption jobs,
        but in principle any value is possible.

Usage:
    Ginfo [options]

Options:
    -U
        Limit output to the current user.

    -u, --user=<NAME>
        Limit output to user(s).
        Option may be repeated. Search by regex.

    -j, --jobid=<NAME>
        Limit output to job-id(s).
        Option may be repeated. Search by regex.

    --host=<NAME>
        Limit output to host(s).
        Option may be repeated. Search by regex.

    -f, --cfree=<NAME>
        Limit output to free CPU(s).
        Option may be repeated. Search by regex.

    -p, --partition=<NAME>
        Limit output to partition(s).
        Option may be repeated. Search by regex.

    -s, --sort=<NAME>
        Sort by field.
        Option may be repeated. Use header names.

    -r, --reverse
        Reverse sort.

    -o, --output=<NAME>
        Select output columns.
        Option may be repeated. Use header names.

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

    --sep=<NAME>
        Set column separator. [default: " "]

    --long
        Print full information (each column is printed as a line).

    --debug=<FILE> <FILE>
        Debug: read ``sinfo -o "%all"`` and  ``squeue -o "%all"`` from file.

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

import numpy as np

from . import rich
from . import sinfo
from . import squeue
from . import table
from . import version


def main():
    # -- parse command line arguments --

    class Parser(argparse.ArgumentParser):
        def print_help(self):
            print(__doc__)

    parser = Parser()
    parser.add_argument("-U", action="store_true")
    parser.add_argument("-u", "--user", type=str, action="append", default=[])
    parser.add_argument("-j", "--jobid", type=str, action="append")
    parser.add_argument("--host", type=str, action="append")
    parser.add_argument("-c", "--cfree", type=str, action="append")
    parser.add_argument("-p", "--partition", type=str, action="append")
    parser.add_argument("-s", "--sort", type=str, action="append")
    parser.add_argument("-r", "--reverse", action="store_true")
    parser.add_argument("-o", "--output", type=str, action="append")
    parser.add_argument("-S", "--summary", action="store_true")
    parser.add_argument("--no-header", action="store_true")
    parser.add_argument("--no-truncate", action="store_true")
    parser.add_argument("--width", type=int)
    parser.add_argument("--colors", type=str, default="dark")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("--sep", type=str, default=" ")
    parser.add_argument("--long", action="store_true")
    parser.add_argument("--debug", type=str, nargs=2)
    parser.add_argument("--version", action="version", version=version)
    args = vars(parser.parse_args())

    # -------------------------------- field-names and print settings --------

    # conversion map: default field-names -> custom field-names
    alias = {
        "HOSTNAMES": "Host",
        "CPUS_T": "CPUs",
        "CPUS_I": "Cfree",
        "CPUS_D": "Cdown",
        "CPUS_O": "Con",
        "CPU_RELJOB": "CPU%",
        "PARTITION": "Partition",
        "MEMORY": "Mem",
        "FREE_MEM": "Mfree",
        "MEM_RELJOB": "Mem%",
        "TIMELIMIT": "Tlim",
        "STATE": "State",
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
        {"key": "HOSTNAMES", "width": 4, "align": "<", "priority": True},
        {"key": "CPUS_T", "width": 4, "align": ">", "priority": True},
        {"key": "CPUS_I", "width": 5, "align": ">", "priority": True},
        {"key": "CPU_RELJOB", "width": 4, "align": ">", "priority": True},
        {"key": "MEMORY", "width": 3, "align": ">", "priority": True},
        {"key": "FREE_MEM", "width": 5, "align": ">", "priority": True},
        {"key": "MEM_RELJOB", "width": 4, "align": ">", "priority": True},
        {"key": "PARTITION", "width": 9, "align": "<", "priority": True},
        {"key": "TIMELIMIT", "width": 4, "align": ">", "priority": False},
        {"key": "STATE", "width": 5, "align": "<", "priority": False},
    ]

    # header
    header = {
        column["key"]: rich.String(alias[column["key"]], align=column["align"])
        for column in columns
    }

    # print settings for the summary
    columns_summary = [
        {"key": "PARTITION", "width": 9, "align": "<", "priority": True},
        {"key": "CPUS_T", "width": 4, "align": ">", "priority": True},
        {"key": "CPUS_O", "width": 5, "align": ">", "priority": True},
        {"key": "CPUS_D", "width": 5, "align": ">", "priority": True},
        {"key": "CPUS_I", "width": 5, "align": ">", "priority": True},
        {"key": "CPU_RELJOB", "width": 4, "align": ">", "priority": True},
        {"key": "MEM_RELJOB", "width": 4, "align": ">", "priority": True},
    ]

    # header
    header_summary = {
        column["key"]: rich.String(alias[column["key"]], align=column["align"])
        for column in columns_summary
    }

    # select color theme
    theme = sinfo.colors(args["colors"].lower())

    # -- load the output of "sinfo" --

    if not args["debug"]:
        lines = sinfo.read_interpret(theme=theme)

    else:
        lines = sinfo.read_interpret(
            data=open(args["debug"][0]).read(),
            theme=theme,
        )

    # ----------------------------- limit based on command-line options ------

    for key in ["HOSTNAMES", "PARTITION", "CPUS_I"]:
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

    # -- support function used below --

    # if needed, convert 'name[10-14,16]' to 'list(name10, name11, name12, name13, name14, name16)'
    def expand_nodelist(text):
        # try to split 'name', '[10-14]'
        match = list(filter(None, re.split(r"(\[[^\]]*\])", text)))

        # no split made: no need to interpret anything, return as list
        if len(match) == 1:
            return [text]

        # split in variables
        name, numbers = match

        # remove brackets '[10-14,16]' -> '10-14,16'
        numbers = numbers[1:-1]

        # split '10-14,16' -> list('10-14', '16')
        numbers = numbers.split(",")

        # allocate output
        nodes = []

        # expand if needed
        for number in numbers:
            # '16' -> 'name16'
            if len(number.split("-")) == 1:
                # copy to list
                nodes += [name + number]

            # '10-14' -> list('name10', 'name11', 'name12', 'name13', 'name14')
            else:
                # get start and end numbers
                start, end = number.split("-")

                # expand between beginning and end
                nodes += [
                    name + ("%0" + str(len(start)) + "d") % i
                    for i in range(int(start), int(end) + 1)
                ]

        # return output
        return nodes

    # -- limit to users --

    # handle 'alias' options
    if args["U"]:
        args["user"] += [pwd.getpwuid(os.getuid())[0]]

    # apply filter
    if args["user"] or args["jobid"]:
        # get list of jobs
        # ----------------

        # read
        if not args["debug"]:
            jobs = squeue.read_interpret()

        else:
            jobs = squeue.read_interpret(
                data=open(args["debug"][1]).read(),
                now=os.path.getctime(args["debug"][1]),
            )

        # limit to running jobs
        jobs = [j for j in jobs if str(j["ST"]) == "R"]

        # limit to users' jobs
        if args["user"]:
            jobs = [
                str(j["NODELIST"])
                for j in jobs
                if sum(1 if re.match(n, str(j["USER"])) else 0 for n in args["user"])
            ]

        # limit to specific jobs
        if args["jobid"]:
            jobs = [
                str(j["NODELIST"])
                for j in jobs
                if sum(1 if re.match(n, str(j["JOBID"])) else 0 for n in args["jobid"])
            ]

        # get list of nodes for the users' jobs
        # --

        # allocate list of nodes
        nodes = []

        # loop over jobs
        for job in jobs:
            # simple name (e.g. 'f123') -> add to list
            if len(job.split(",")) == 1:
                nodes += expand_nodelist(job)
                continue

            # split all array jobs, e.g.
            # g117,g[123-456],f[023-025] -> ('g117,g', '[123-456]', ',f', '[023-025]')
            match = list(filter(None, re.split(r"(\[[^\]]*\])", job)))

            # loop over arrays
            for name, numbers in zip(match[0::2], match[1::2]):
                # strip plain jobs that are still prepending the array
                name = name.split(",")
                # add plain jobs to node-list
                nodes += name[:-1]
                # interpret all batch jobs and add to node-list
                nodes += expand_nodelist(name[-1] + numbers)

        # filter empty items
        nodes = list(filter(None, nodes))

        # limit data
        lines = [line for line in lines if str(line["HOSTNAMES"]) in nodes]

        # color-highlight selected columns
        # - apply to all remaining lines
        for line in lines:
            line["HOSTNAMES"].color = theme["selection"]
        # - apply to the header
        header["HOSTNAMES"].color = theme["selection"]

    # -- sort --

    if args["sort"]:
        sortkeys = [aliasInv[key.upper()] for key in args["sort"]]
    else:
        sortkeys = ["HOSTNAMES", "PARTITION"]

    idx = np.lexsort([[i[key] for i in lines] for key in sortkeys])
    if args["reverse"]:
        idx = idx[::-1]
    lines = [lines[i] for i in idx]

    # -- select columns --

    if args["output"]:
        keys = [aliasInv[key.upper()] for key in args["output"]]

        columns = [column for column in columns if column["key"] in keys]

    # -- print --

    if not args["summary"]:
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
                lines=lines,
                columns=columns,
                header=header,
                no_truncate=args["no_truncate"],
                sep=args["sep"],
                width=args["width"],
                print_header=not args["no_header"],
            )

            sys.exit(0)

    # -- summarize information --

    # get names of the different partitions
    partitions = sorted({str(line["PARTITION"]) for line in lines})

    # start a new list of "node information", summed on the relevant nodes
    partitions = [{"PARTITION": rich.String(key)} for key in partitions]

    # loop over partitions
    for partition in partitions:
        # - isolate nodes for this partition
        N = [line for line in lines if str(line["PARTITION"]) == str(partition["PARTITION"])]

        # - get the CPU count
        partition["CPUS_T"] = rich.Integer(sum(int(line["CPUS_T"]) for line in N))
        partition["CPUS_O"] = rich.Integer(sum(int(line["CPUS_O"]) for line in N))
        partition["CPUS_D"] = rich.Integer(sum(int(line["CPUS_D"]) for line in N))
        partition["CPUS_I"] = rich.Integer(sum(int(line["CPUS_I"]) for line in N))

        # - initialize scores
        partition["CPU_RELJOB"] = rich.Float("")
        partition["MEM_RELJOB"] = rich.Float("")

        # - average load
        if len([1 for line in N if line["CPU_RELJOB"].isnumeric()]) > 0:
            partition["CPU_RELJOB"] = rich.Float(
                sum(float(line["CPU_RELJOB"]) for line in N if line["CPU_RELJOB"].isnumeric())
                / sum(1.0 for line in N if line["CPU_RELJOB"].isnumeric())
            )

        # - average memory consumption
        if len([1 for line in N if line["MEM_RELJOB"].isnumeric()]) > 0:
            partition["MEM_RELJOB"] = rich.Float(
                sum(float(line["MEM_RELJOB"]) for line in N if line["MEM_RELJOB"].isnumeric())
                / sum(1.0 for line in N if line["MEM_RELJOB"].isnumeric())
            )

        # - highlight 'scores'
        if int(partition["CPUS_I"]) > 0:
            partition["CPUS_I"].color = theme["free"]
        if float(partition["CPU_RELJOB"]) > 1.05:
            partition["CPU_RELJOB"].color = theme["warning"]
        elif float(partition["CPU_RELJOB"]) < 0.95:
            partition["CPU_RELJOB"].color = theme["low"]

    # rename field
    lines = partitions

    # -- sort --

    # default sort
    lines.sort(key=lambda line: line["PARTITION"], reverse=args["reverse"])

    # optional: sort by key(s)
    if args["sort"]:
        keys = [alias[column["key"]].upper() for column in columns_summary]
        args["sort"] = [key for key in args["sort"] if key.upper() in keys]

        idx = np.lexsort([[i[aliasInv[k.upper()]] for i in lines] for k in args["sort"]])
        if args["reverse"]:
            idx = idx[::-1]
        lines = [lines[i] for i in idx]

    # -- print --

    table.print_columns(
        lines=lines,
        columns=columns_summary,
        header=header_summary,
        no_truncate=args["no_truncate"],
        sep=args["sep"],
        width=args["width"],
        print_header=not args["no_header"],
    )
