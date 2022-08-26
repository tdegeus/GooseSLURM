import argparse
import json


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


def cli_parser(cli_args: list[str] = None):
    """
    Parse command-line arguments.
    :param cli_args: Specify command-line arguments. Default: ``sys.argv[1:]``.
    :return: The result of parsing.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("jobs", type=int, nargs="*")

    if cli_args is None:
        return parser.parse_args()

    return parser.parse_args(cli_args)


def cli_main(cli_args: list[str] = None):
    """
    Main function for the command-line interface.
    :param cli_args: Specify command-line arguments. Default: ``sys.argv[1:]``.
    """

    args = cli_parser(cli_args)

    for jobid in args.jobs:
        for line in read(jobid):
            line = {k: v for k, v in line.items() if len(v) > 0}
            json_object = json.dumps(line, indent=4)
            print(json_object)
