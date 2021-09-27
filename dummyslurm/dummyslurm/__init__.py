import argparse
import yaml
import os

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

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "args",
        nargs="*"
    )

    args = parser.parse_args()

    print("Submitted batch job {:d}".format(log["jobid"]))

    log["commands"] += [args.args]
    log["jobid"] += 1

    with open(logfile, "w") as file:
        yaml.dump(log, file)






