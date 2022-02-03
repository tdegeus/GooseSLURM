import os
import sys

import yaml

version = "1.2.3"

dirname = os.path.dirname(os.path.abspath(__file__))


def sbatch():

    logfile = "_sbatch.yaml"
    log = dict(
        jobid=1,
        commands=[],
    )

    if os.path.isfile(os.path.realpath(logfile)):
        with open(logfile) as file:
            log = yaml.load(file.read(), Loader=yaml.FullLoader)

    print("Submitted batch job {:d}".format(log["jobid"]))

    log["commands"] += [sys.argv[1:]]
    log["jobid"] += 1

    with open(logfile, "w") as file:
        yaml.dump(log, file)


def sacct():

    if sys.argv[1:] == ["-l", "-j", "1"]:
        with open(os.path.join(dirname, "sacct_-l_-j_1.txt"), "r") as file:
            print(file.read())
        return

    raise OSError("Command not implemented")
