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
    parser.add_argument("-d", "--dependency", type=int)
    parser.add_argument("-J", "--job-name", type=str)
    parser.add_argument("-N", "--nodes", type=str, default="1")
    parser.add_argument("-n", "--ntasks", type=str, default="1")
    parser.add_argument("-p", "--partition", type=str, default="serial")
    parser.add_argument("-t", "--time", type=str, default="1:00:00")
    parser.add_argument("--mem", type=str, default="5000000000")
    parser.add_argument("--chdir", type=str)
    args = parser.parse_args()

    if args.job_name is None:
        args.job_name = args.script

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
    mylog = vars(args).copy()
    for key, value in dict(mylog).items():
        if value is None:
            del mylog[key]

    mylog["state"] = "PD"
    mylog["jobid"] = jobid
    mylog["user"] = pwd.getpwuid(os.getuid())[0]
    mylog["command"] = os.path.abspath(mylog["script"])
    if args.chdir:
        mylog["workdir"] = args.chdir
    else:
        mylog["workdir"] = os.path.dirname(os.path.abspath(mylog["script"]))

    log += [mylog]

    print(f"Submitted batch job {jobid:d}")

    with open(logfile, "w") as file:
        yaml.dump(log, file)


def scancel():
    """
    Dummy ``scancel`` command.
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
    parser.add_argument("jobid", type=int, nargs="*")
    args = parser.parse_args()

    log = [i for i in log if i["jobid"] not in args.jobid]

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
            "CPUS": "cpus_per_task",
            "DEPENDENCY": "dependency",
            "JOBID": "jobid",
            "MIN_MEMORY": "mem",
            "NAME": "job_name",
            "NODES": "nodes",
            "PARTITION": "partition",
            "ST": "state",
            "TIME": "time",
            "USER": "user",
            "WORK_DIR": "workdir",
        }

        print("|".join([i.upper() for i in keys]))

        for i in log:
            print("|".join([str(i.get(alias.get(key, "NONE"), "N/A")) for key in keys]))

        return 0

    raise OSError("Command not implemented")


def scontrol():

    log = []

    if os.path.isfile(os.path.realpath(logfile)):
        with open(logfile) as file:
            log = yaml.load(file.read(), Loader=yaml.FullLoader)

    if re.match(r"^(show job )([0-9]*)", " ".join(sys.argv[1:])):

        jobid = int(re.split(r"^(show job )([0-9]*)", " ".join(sys.argv[1:]))[2])

        keys = [
            "JobId",
            "JobName",
            "UserId",
            "GroupId",
            "MCS_label",
            "Priority",
            "Nice",
            "Account",
            "QOS",
            "JobState",
            "Reason",
            "Dependency",
            "Requeue",
            "Restarts",
            "BatchFlag",
            "Reboot",
            "ExitCode",
            "RunTime",
            "TimeLimit",
            "TimeMin",
            "SubmitTime",
            "EligibleTime",
            "AccrueTime",
            "StartTime",
            "EndTime",
            "Deadline",
            "SuspendTime",
            "SecsPreSuspend",
            "LastSchedEval",
            "Partition",
            "AllocNode:Sid",
            "ReqNodeList",
            "ExcNodeList",
            "NodeList",
            "BatchHost",
            "NumNodes",
            "NumCPUs",
            "NumTasks",
            "CPUs/Task",
            "ReqB:S:C:T",
            "TRES",
            "Socks/Node",
            "NtasksPerN:B:S:C",
            "CoreSpec",
            "MinCPUsNode",
            "MinMemoryCPU",
            "MinTmpDiskNode",
            "Features",
            "DelayBoot",
            "OverSubscribe",
            "Contiguous",
            "Licenses",
            "Network",
            "Command",
            "WorkDir",
            "StdErr",
            "StdIn",
            "StdOut",
            "Power",
        ]

        alias = {
            "Account": "account",
            "Command": "command",
            "JobId": "jobid",
            "JobName": "job_name",
            "UserId": "user",
        }

        for i in log:
            if i["jobid"] == jobid:
                ret = [f"{key}=" + str(i.get(alias.get(key, "NONE"), "")) for key in keys]
                ret = textwrap.wrap(" ".join(ret), subsequent_indent="    ", break_long_words=False)
                ret = "\n".join(ret)
                print(ret)
                return 0

        raise OSError("JobID not found")

    raise OSError("Command not implemented")


def sacct():

    args = sys.argv[1:]
    log = []

    if os.path.isfile(os.path.realpath(logfile)):
        with open(logfile) as file:
            log = yaml.load(file.read(), Loader=yaml.FullLoader)

    allocations = False
    if "-X" in sys.argv[1:]:
        allocations = True
        args.remove("-X")

    if re.match(r"^(-p -l -j )([0-9\,]*)", " ".join(args)):

        jobids = map(int, re.split(r"^(-p -l -j )([0-9\,]*)", " ".join(args))[2].split(","))

        keys = [
            "JobID",
            "JobIDRaw",
            "JobName",
            "Partition",
            "MaxVMSize",
            "MaxVMSizeNode",
            "MaxVMSizeTask",
            "AveVMSize",
            "MaxRSS",
            "MaxRSSNode",
            "MaxRSSTask",
            "AveRSS",
            "MaxPages",
            "MaxPagesNode",
            "MaxPagesTask",
            "AvePages",
            "MinCPU",
            "MinCPUNode",
            "MinCPUTask",
            "AveCPU",
            "NTasks",
            "AllocCPUS",
            "Elapsed",
            "State",
            "ExitCode",
            "AveCPUFreq",
            "ReqCPUFreqMin",
            "ReqCPUFreqMax",
            "ReqCPUFreqGov",
            "ReqMem",
            "ConsumedEnergy",
            "MaxDiskRead",
            "MaxDiskReadNode",
            "MaxDiskReadTask",
            "AveDiskRead",
            "MaxDiskWrite",
            "MaxDiskWriteNode",
            "MaxDiskWriteTask",
            "AveDiskWrite",
            "AllocGRES",
            "ReqGRES",
            "ReqTRES",
            "AllocTRES",
            "TRESUsageInAve",
            "TRESUsageInMax",
            "TRESUsageInMaxNode",
            "TRESUsageInMaxTask",
            "TRESUsageInMin",
            "TRESUsageInMinNode",
            "TRESUsageInMinTask",
            "TRESUsageInTot",
            "TRESUsageOutMax",
            "TRESUsageOutMaxNode",
            "TRESUsageOutMaxTask",
            "TRESUsageOutAve",
            "TRESUsageOutTot",
        ]

        alias = {
            "JobID": "jobid",
            "JobName": "job_name",
        }

        lines = []

        for i in log:
            if i["jobid"] in jobids:

                base = [str(i.get(alias.get(key, "NONE"), "")) for key in keys]
                batch = [r for r in base]
                extern = [r for r in base]
                batch[0] = batch[0] + ".batch"
                extern[0] = extern[0] + ".extern"
                lines.append("|".join(base) + "|")
                if not allocations:
                    lines.append("|".join(batch) + "|")
                    lines.append("|".join(extern) + "|")

        if len(lines) > 0:
            print("|".join(keys) + "|")
            print("\n".join(lines))
            return 0

        raise OSError("JobID not found")

    raise OSError("Command not implemented")
