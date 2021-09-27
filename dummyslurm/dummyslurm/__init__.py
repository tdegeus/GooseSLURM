import os
import sys

import yaml

version = "1.2.3"


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
