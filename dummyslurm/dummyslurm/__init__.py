import argparse
import inspect
import os
import pwd
import re
import sys
import textwrap

import yaml

version = "1.2.3"

dirname = os.path.dirname(os.path.abspath(__file__))
logfile = "_sbatch.yaml"


def sbatch():
    """
    Dummy ``sbatch`` command.
    A local file '_sbatch.yaml' in the current working directory will contain the history of
    'submitted' jobs.
    """

    log = []

    if os.path.isfile(os.path.realpath(logfile)):
        with open(logfile) as file:
            log = yaml.load(file.read(), Loader=yaml.FullLoader)

    class MyFmt(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.MetavarTypeHelpFormatter,
    ):
        pass

    funcname = inspect.getframeinfo(inspect.currentframe()).function
    doc = textwrap.dedent(inspect.getdoc(globals()[funcname]))

    parser = argparse.ArgumentParser(formatter_class=MyFmt, description=doc)
    parser.add_argument("script", type=str)
    parser.add_argument("-A", "--account", type=str, default="default")
    parser.add_argument("-c", "--cpus-per-task", type=str, default="1")
    parser.add_argument("-J", "--job-name", type=str, default="sbatch")
    parser.add_argument("-N", "--nodes", type=str, default="1")
    parser.add_argument("-n", "--ntasks", type=str, default="1")
    parser.add_argument("-p", "--partition", type=str, default="serial")
    parser.add_argument("-t", "--time", type=str, default="1:00:00")
    parser.add_argument("--mem", type=str, default="5000000000")
    args = parser.parse_args()

    # read SBATCH options from script
    if os.path.isfile(args.script):
        extra = []
        with open(args.script) as file:
            lines = file.read().split("\n")
        for line in lines:
            if re.match("^#SBATCH", line):
                extra += re.split("^#SBATCH", line)[1].strip().rstrip().split(" ")
        if len(extra) > 0:
            args = parser.parse_args(extra + sys.argv[1:])

    jobid = len(log) + 1
    mylog = vars(args)
    mylog["jobid"] = jobid
    mylog["user"] = pwd.getpwuid(os.getuid())[0]
    log += [mylog]
    print(f"Submitted batch job {jobid:d}")

    with open(logfile, "w") as file:
        yaml.dump(log, file)


def squeue():
    """
    Dummy ``squeue`` command.
    Reads from local file '_sbatch.yaml' in the current working directory created using the dummy
    ``sbatch`` command.
    """

    log = []

    if os.path.isfile(os.path.realpath(logfile)):
        with open(logfile) as file:
            log = yaml.load(file.read(), Loader=yaml.FullLoader)

    if sys.argv[1:] == ["-o", "%all"]:
        keys = [
            "ACCOUNT",
            "TRES_PER_NODE",
            "MIN_CPUS",
            "MIN_TMP_DISK",
            "END_TIME",
            "FEATURES",
            "GROUP",
            "OVER_SUBSCRIBE",
            "JOBID",
            "NAME",
            "COMMENT",
            "TIME_LIMIT",
            "MIN_MEMORY",
            "REQ_NODES",
            "COMMAND",
            "PRIORITY",
            "QOS",
            "REASON",
            "ST",
            "USER",
            "RESERVATION",
            "WCKEY",
            "EXC_NODES",
            "NICE",
            "S:C:T",
            "JOBID",
            "EXEC_HOST",
            "CPUS",
            "NODES",
            "DEPENDENCY",
            "ARRAY_JOB_ID",
            "GROUP",
            "SOCKETS_PER_NODE",
            "CORES_PER_SOCKET",
            "THREADS_PER_CORE",
            "ARRAY_TASK_ID",
            "TIME_LEFT",
            "TIME",
            "NODELIST",
            "CONTIGUOUS",
            "PARTITION",
            "PRIORITY",
            "NODELIST(REASON)",
            "START_TIME",
            "STATE",
            "UID",
            "SUBMIT_TIME",
            "LICENSES",
            "CORE_SPEC",
            "SCHEDNODES",
            "WORK_DIR",
        ]
        alias = {
            "ACCOUNT": "account",
            "PARTITION": "partition",
            "CPUS": "cpus_per_task",
            "NODES": "nodes",
            "MIN_MEMORY": "mem",
            "USER": "user",
        }
        print("|".join([i.upper() for i in keys]))
        for i in log:
            print("|".join([i.get(alias.get(key, "NONE"), "N/A") for key in keys]))
        return 0

    raise OSError("Command not implemented")


def sacct():

    if sys.argv[1:] == ["-l", "-j", "1"]:
        with open(os.path.join(dirname, "sacct_-l_-j_1.txt")) as file:
            print(file.read())
        return 0

    raise OSError("Command not implemented")
