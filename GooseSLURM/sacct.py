import argparse
import json
import sys

from . import table
from . import rich
from ._version import version


def read(jobid: int | str) -> list[dict]:
    r"""
    Read ``sacct -p -l -j jobid`.

    :param jobid: The jobid to read.
    :return: List of dictionaries, that contain the different fields. All data are strings.
    """

    import subprocess

    # get live info
    data = subprocess.check_output(f"sacct -p -l -j {str(jobid)}", shell=True).decode("utf-8")

    # extract the header and the info
    head, data = data.split("\n", 1)
    data = list(filter(None, data.split("\n")))

    # get the field-names
    head = head.split("|")

    # convert to list of dictionaries
    # - initialize
    lines = []
    # - loop over lines
    for line in data:
        # -- initialize empty dictionary
        info = {}
        # -- fill dictionary
        for key, val in zip(head, line.split("|")):
            if len(key.strip()) > 0:
                info[key.strip()] = val.strip()
        # -- store to list of lines
        lines += [info]

    return lines


def cli_parser() -> argparse.ArgumentParser:
    """
    Return parser of command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Display available information from ``sacct -j jobid`` (in JSON format)."
    )
    parser.add_argument("--sep", type=str, default=" ", help="Column spearator.")
    parser.add_argument("-j", "--json", action="store_true", help="Print in JSON format.")
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

    lines = []
    for jobid in args.jobid:
        for line in read(jobid):
            lines += [line]

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
        "WorkDir",
    ]

    columns = [{"key": key, "width": len(key), "align": ">", "priority": True} for key in default]
    header = {key: key for key in default}

    for i in range(len(lines)):
        for key in ["Elapsed", "CPUTime"]:
            lines[i][key] = rich.Duration(lines[i][key])

    table.print_columns(lines, columns, header, sep=args.sep)




def _Gacct_catch():
    try:
        Gacct(sys.argv[1:])
    except Exception as e:
        print(e)
        return 1
