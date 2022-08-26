import argparse
import json
import sys


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

    parser = argparse.ArgumentParser()
    parser.add_argument("jobid", type=int, nargs="*", help="JobID(s) to read.")
    return parser


def Gacct(args: list[str]):
    """
    Command-line tool to print datasets from a file, see ``--help``.
    :param args: Command-line arguments (should be all strings).
    """

    parser = cli_parser()
    args = parser.parse_args(args)

    for jobid in args.jobs:
        for line in read(jobid):
            line = {k: v for k, v in line.items() if len(v) > 0}
            json_object = json.dumps(line, indent=4)
            print(json_object)


def _Gacct_catch():
    try:
        Gacct(sys.argv[1:])
    except Exception as e:
        print(e)
        return 1
