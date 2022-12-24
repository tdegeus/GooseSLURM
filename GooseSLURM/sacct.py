from __future__ import annotations

import argparse
import datetime
import json
import os
import pwd
import re
import subprocess
import sys
from collections import defaultdict

import numpy as np

from . import duration
from . import rich
from . import table
from ._version import version


def _read(cmd: str) -> list[dict]:
    r"""
    Read command and interpret.
    Requires ``-p`` and ``-l``.

    :param jobid: The jobid to read.
    :return: List of dictionaries, that contain the different fields. All data are strings.
    """

    data = subprocess.check_output(cmd, shell=True).decode("utf-8")

    head, data = data.split("\n", 1)
    data = list(filter(None, data.split("\n")))
    head = head.split("|")

    lines = []
    for line in data:

        info = {}

        for key, val in zip(head, line.split("|")):
            if len(key.strip()) > 0:
                info[key.strip()] = val.strip()

        lines += [info]

    return lines


def read_job(jobid: int | str) -> list[dict]:
    r"""
    Read ``sacct -p -l -j jobid`.

    :param jobid: The jobid to read.
    :return: List of dictionaries, that contain the different fields. All data are strings.
    """

    return _read(f"sacct -p -l -j {str(jobid)}")


def _asdate(text: str):

    if text[0] != "-":
        return text

    d = datetime.datetime.now() - datetime.timedelta(seconds=duration.asSeconds(text[1:]))
    return d.strftime("%Y-%m-%dT%H:%M:%S")


def cli_parser() -> argparse.ArgumentParser:
    """
    Return parser of command-line arguments.
    """

    help = """
    Display available information from ``sacct -j jobid...`` or ``sacct [OPTION]``.

    *   The time fields can be specified as rich
        (e.g. ``-S="-1h"`` for jobs that started at maximum one hour ago)
        in addition to the default format of ``sacct``.

    *   As state use: running / r, completed / cd, failed / f, timeout / to,
        resizing / rs, deadline / dl, node_fail / nf.

    *   The output can be returned in JSON format (``--json``).

    *   Extra columns can be added (``--extra``), see ``sacct --helpformat``.
        Commonly used are ``--extra="WorkDir"``.

    *   The following column abbreviations are used (depending on the output):
        -  ``State``: ``ST``
        -  ``ExitCode``: ``exit``

    .. tip::

        Use ``seff jobid`` to get more information, such as memory usage.
    """

    parser = argparse.ArgumentParser(
        description=help,
    )

    append = dict(type=str, action="append", default=[])
    parser.add_argument("-X", "--allocations", action="store_true", help="Include only main job.")
    parser.add_argument("-j", "--json", action="store_true", help="Print in JSON format.")
    parser.add_argument("--sep", type=str, default=" ", help="Column separator.")
    parser.add_argument("--no-truncate", action="store_true", help="Print without fitting screen.")
    parser.add_argument("--sort", help="Sort based on column.", **append)
    parser.add_argument("--reverse", action="store_true", help="Reverse order.")
    parser.add_argument("--no-header", action="store_true", help="Do not print header.")
    parser.add_argument("--width", type=int, help="Print width (default: read from terminal).")
    parser.add_argument("-o", "--output", type=str, action="append", help="Output columns.")
    parser.add_argument("--infer", type=str, help="Read extra data from ``JOBID.infer``.")
    parser.add_argument("-e", "--extra", help="Extra columns.", **append)
    parser.add_argument(
        "--abspath", action="store_true", help="Print directories as absolute (default: automatic)."
    )
    parser.add_argument(
        "--relpath", action="store_true", help="Print directories as relative (default: automatic)."
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Filter jobs whose WorkDir has this root (WorkDir printed relative to this root).",
    )
    parser.add_argument(
        "-L", "--allclusters", action="store_true", help="Display jobs ran on all clusters."
    )
    parser.add_argument(
        "-a", "--allusers", action="store_true", help="All users (default: only current user)."
    )
    parser.add_argument("-T", "--truncate", action="store_true", help="Truncate time.")
    parser.add_argument("-S", "--starttime", type=str, help="Job started after time.")
    parser.add_argument("-E", "--endtime", type=str, help="Job end before time.")
    parser.add_argument("-i", "--nnodes", type=str, help="Jobs which ran on this many nodes.")
    parser.add_argument("-I", "--ncpus", type=str, help="Jobs which ran on this many cpus.")
    parser.add_argument(
        "-k", "--timelimit-min", type=str, help="Only send data about jobs with this timelimit."
    )
    parser.add_argument(
        "-K", "--timelimit-max", type=str, help="Only send data about jobs with this timelimit."
    )
    parser.add_argument("-r", "--partition", help="(Comma separated list of) partitions.", **append)
    parser.add_argument("-s", "--state", help="Select state(s).", **append)
    parser.add_argument("-N", "--nodelist", help="Select nodelist(s).", **append)
    parser.add_argument("-M", "--clusters", help="Select cluster(s).", **append)
    parser.add_argument("-A", "--account", help="Select account(s).", **append)
    parser.add_argument("-u", "--user", help="Select username(s).", **append)
    parser.add_argument("--uid", help="Select user-id(s).", **append)
    parser.add_argument("-U", action="store_true", help="Select current user.")
    parser.add_argument("-g", "--group", help="Select group(s).", **append)
    parser.add_argument("--gid", help="Select group-id(s).", **append)
    parser.add_argument("--name", help="Select job-name(s).", **append)
    parser.add_argument("-q", "--qos", help="Select qos(s).", **append)
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument("jobid", type=int, nargs="*", help="JobID(s) to read.")
    return parser


def Gacct(args: list[str]):
    """
    Command-line tool to print datasets from a file, see ``--help``.
    :param args: Command-line arguments (should be all strings).
    """

    parser = cli_parser()
    args = parser.parse_args(args)
    extra = [i for i in args.extra]

    if args.root is not None:
        if "WorkDir" not in extra:
            extra += ["WorkDir"]

    opts = ["-p", "-l"]
    if args.allocations:
        opts += ["-X"]
    if args.allusers:
        opts += ["-a"]
    if args.allclusters:
        opts += ["-A"]
    if args.truncate:
        opts += ["-T"]
    if args.starttime:
        opts += ["-S", _asdate(args.starttime)]
    if args.endtime:
        opts += ["-E", _asdate(args.endtime)]
    if args.nnodes:
        opts += ["-i", args.nnodes]
    if args.ncpus:
        opts += ["-I", args.ncpus]
    if args.timelimit_min:
        opts += ["-k", duration.asSlurm(args.timelimit_min)]
    if args.timelimit_max:
        opts += ["-K", duration.asSlurm(args.timelimit_max)]
    if args.partition:
        opts += ["-r", ",".join(args.partition)]
    if args.nodelist:
        opts += ["-N", ",".join(args.nodelist)]
    if args.clusters:
        opts += ["-M", ",".join(args.clusters)]
    if args.account:
        opts += ["-A", ",".join(args.account)]
    if args.qos:
        opts += ["-q", ",".join(args.qos)]
    if args.jobid:
        opts += ["-j", ",".join(map(str, args.jobid))]

    if args.name:
        vec = [["--name", i] for i in args.name]
        opts += [num for elem in vec for num in elem]

    if args.U:
        opts += ["-u", pwd.getpwuid(os.getuid())[0]]
    elif args.user and args.uid:
        opts += ["-u", ",".join(args.user) + "," + ",".join(args.uid)]
    elif args.user:
        opts += ["-u", ",".join(args.user)]
    elif args.uid:
        opts += ["-u", ",".join(args.uid)]

    if args.group and args.gid:
        opts += ["-u", ",".join(args.group) + "," + ",".join(args.gid)]
    elif args.group:
        opts += ["-u", ",".join(args.group)]
    elif args.gid:
        opts += ["-u", ",".join(args.gid)]

    lines = _read(" ".join(["sacct"] + opts))

    if extra:
        op = [i for i in opts] + ["--format", ",".join(extra)]
        op.remove("-l")
        ex = _read(" ".join(["sacct"] + op))
        for i in range(len(lines)):
            lines[i] = {**lines[i], **ex[i]}

    if args.root:
        lines = [i for i in lines if not os.path.relpath(i["WorkDir"], args.root).startswith("..")]
        for line in lines:
            line["WorkDir"] = os.path.relpath(line["WorkDir"], args.root)
    elif "WorkDir" in extra:
        if args.abspath:
            for line in lines:
                line["WorkDir"] = os.path.abspath(line["WorkDir"])
        elif args.relpath:
            for line in lines:
                line["WorkDir"] = os.path.relpath(line["WorkDir"])
        else:
            for line in lines:
                if len(os.path.relpath(line["WorkDir"]).split("../")) < 3:
                    line["WorkDir"] = os.path.relpath(line["WorkDir"])

    if args.infer:
        if not args.allocations:
            raise ValueError("Cannot infer extra data without --allocations.")
        opts.remove("-X")
        ex = _read(" ".join(["sacct"] + opts))
        data = defaultdict(dict)
        for line in ex:
            if "." not in line["JobID"]:
                continue
            jobid, key = line["JobID"].split(".")
            data[key][jobid] = line
        for line in lines:
            for key in line:
                if len(line[key]) == 0:
                    if line["JobID"] in data[args.infer]:
                        line[key] = data[args.infer][line["JobID"]][key]

    if args.state:
        alias = {
            "r": "RUNNING",
            "running": "RUNNING",
            "cd": "COMPLETED",
            "c": "COMPLETED",
            "completed": "COMPLETED",
            "f": "FAILED",
            "failed": "FAILED",
            "to": "TIMEOUT",
            "timeout": "TIMEOUT",
            "rs": "RESIZING",
            "resizing": "RESIZING",
            "dl": "DEADLINE",
            "deadline": "DEADLINE",
            "nf": "NODE_FAIL",
            "node_fail": "NODE_FAIL",
        }
        keys = []
        for i in args.state:
            for j in i.split(","):
                keys.append(j)
                if j not in alias:
                    alias[j] = j
        key = "State"
        fields = [alias[i] for i in keys]
        lines = [
            line
            for line in lines
            if sum(1 if re.match(n, str(line[key]), re.IGNORECASE) else 0 for n in fields)
        ]

    if args.sort:
        lookup = {i.upper(): i for i in lines[0].keys()}
        idx = np.lexsort([[line[lookup[key.upper()]] for line in lines] for key in args.sort])
        if args.reverse:
            idx = idx[::-1]
        lines = [lines[i] for i in idx]
    elif args.reverse:
        lines = [i for i in lines[::-1]]

    if args.json:
        for line in lines:
            line = {k: v for k, v in line.items() if len(v) > 0}
            json_object = json.dumps(line, indent=4)
            print(json_object)
        return

    default = [
        "JobID",
        "User",
        "Account",
        "JobName",
        "State",
        "Partition",
        "Elapsed",
        "ExitCode",
        "Reason",
        "Priority",
        "CPUTime",
        "AveCPU",
        "AveDiskRead",
        "AveDiskWrite",
        "MaxVMSizeNode",
        "MaxVMSize",
    ] + extra
    default = sorted(set(default), key=lambda x: default.index(x))

    columns = [{"key": key, "width": len(key), "align": ">", "priority": True} for key in default]
    header = {key: key for key in default}
    columns[default.index("AveCPU")]["priority"] = False
    columns[default.index("AveDiskRead")]["priority"] = False
    columns[default.index("AveDiskWrite")]["priority"] = False
    columns[default.index("MaxVMSize")]["priority"] = False
    columns[default.index("MaxVMSizeNode")]["priority"] = False
    columns[default.index("JobName")]["align"] = "<"
    columns[default.index("State")]["align"] = "<"
    columns[default.index("Partition")]["align"] = "<"
    if "WorkDir" in extra:
        columns[default.index("WorkDir")]["align"] = "<"

    for i in range(len(lines)):
        for key in ["Elapsed", "CPUTime", "AveCPU"]:
            if key in lines[i]:
                lines[i][key] = rich.Duration(lines[i][key])
        for key in ["AveDiskRead", "AveDiskWrite", "MaxVMSize", "MaxRSS"]:
            if key in lines[i]:
                lines[i][key] = rich.Memory(lines[i][key])

    if len(lines) > 0:
        keep = [False for _ in default]
        for i, key in enumerate(default):
            for line in lines:
                if key not in line:
                    continue
                if len(line[key]) > 0:
                    keep[i] = True
                    continue
        columns = [c for c, k in zip(columns, keep) if k]
        default = [c for c, k in zip(default, keep) if k]

    if args.output:
        keys = [key.upper() for key in args.output]
        columns = [column for column in columns if column["key"] in keys]

    table.print_columns(
        lines=lines,
        columns=columns,
        header=header,
        sep=args.sep,
        no_truncate=args.no_truncate,
        width=args.width,
        print_header=not args.no_header,
    )


def _Gacct_catch():
    Gacct(sys.argv[1:])
