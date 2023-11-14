import re

from . import rich


def colors(theme=None):
    r"""
    Return dictionary of colors.

    .. code-block:: python

        {
            'selection' : '...',
            'free'      : '...',
            'error'     : '...',
            'warning'   : '...',
            'low'       : '...',
        }

    :options:

        **theme** ([``'dark'``] | ``<str>``)
            Select color-theme.
    """

    if theme == "dark":
        return {
            "selection": "1;32;40",
            "free": "1;32",
            "error": "9;31",
            "warning": "1;31",
            "low": "1;36",
        }

    return {
        "selection": "",
        "free": "",
        "error": "",
        "warning": "",
        "low": "",
    }


def read(data=None):
    r"""
    Read ``sinfo -o "%all"``.

    :options:

        **data** (``<str>``)
            For debugging: specify the output of ``sinfo -o "%all"`` as string.

    :returns:

        **lines** ``<list<dict>>``
            A list of dictionaries, that contain the different fields. All data are strings.
    """

    import subprocess

    # get live info
    if data is None:
        data = subprocess.check_output('sinfo -o "%all"', shell=True).decode("utf-8")

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

    # return output
    return lines


def cpu_score(CPU_LOAD, CPUS_A, **kwargs):
    if not CPU_LOAD.isnumeric():
        return rich.Float("")
    if int(CPUS_A) <= 0:
        return rich.Float("")

    return rich.Float(float(CPU_LOAD) / float(CPUS_A), precision=2)


def mem_score(MEMORY, FREE_MEM, CPUS_A, CPUS_T, **kwargs):
    if not FREE_MEM.isnumeric():
        return rich.Float("")
    if not CPUS_T.isnumeric():
        return rich.Float("")
    if int(MEMORY) <= 0:
        return rich.Float("")
    if int(CPUS_A) <= 0:
        return rich.Float("")

    MEM_USED = float(MEMORY) - float(FREE_MEM)

    return rich.Float(float(MEM_USED) / float(MEMORY) * float(CPUS_T) / float(CPUS_A), precision=2)


def interpret(lines, theme=colors()):
    r"""
    Interpret the output of ``GooseSLURM.sinfo.read``. All fields are converted to the
    ``GooseSLURM.rich`` classes adding useful colors in the process.

    :arguments:

        **lines** ``<list<dict>>``
            The output of ``GooseSLURM.sinfo.read``

    :options:

        **theme** (``<dict>``)
            The color-theme, as selected by ``GooseSLURM.sinfo.colors``.

    :returns:

        **lines** (``<list<dict>>``)
            A list of dictionaries, that contain the different fields. All data are
            ``GooseSLURM.rich.String`` or derived types.
    """

    # interpret input as list
    if not isinstance(lines, list):
        lines = [lines]

    # loop over all lines
    for line in lines:
        # convert fields to string
        for key in line:
            if not isinstance(line[key], rich.String):
                line[key] = rich.String(line[key])

                # covert to float
        for key in ["CPU_LOAD"]:
            line[key] = rich.Float(str(line[key]))

        # "days-hours:mins:secs" (e.g. "1-4:18:13") -> seconds
        for key in ["TIMELIMIT"]:
            line[key] = rich.Duration(str(line[key]))

        # convert memory (e.g. "4G") -> bytes
        for key in ["MEMORY", "FREE_MEM"]:
            line[key] = rich.Memory(str(line[key]), default_unit=1e6)

        # CPUs
        # - split: allocated/idle/other/total
        a, i, o, t = str(line["CPUS(A/I/O/T)"]).split("/")
        # - store extra fields
        line["CPUS_A"] = rich.Integer(a)
        line["CPUS_I"] = rich.Integer(i)
        line["CPUS_O"] = rich.Integer(o)
        line["CPUS_T"] = rich.Integer(t)

        # compute scores
        line["CPU_RELJOB"] = cpu_score(**line)
        line["MEM_RELJOB"] = mem_score(**line)

        # default: CPUs down/online
        line["CPUS_D"] = rich.Integer(0)
        line["CPUS_O"] = rich.Integer(str(line["CPUS_T"]))

        # node down: mark all fields
        if (
            re.match(r"down,*", str(line["STATE"]))
            or re.match(r"maint.*", str(line["STATE"]))
            or re.match(r"drain.*", str(line["STATE"]))
        ):
            line["CPUS_I"] = rich.Integer(0)
            line["CPUS_D"] = rich.Integer(str(line["CPUS_T"]))
            line["CPUS_O"] = rich.Integer(0)

            for key in line:
                line[key].color = theme["error"]

        # highlight 'scores'
        if int(line["CPUS_I"]) > 0:
            line["CPUS_I"].color = theme["free"]
        if float(line["CPU_RELJOB"]) > 1.05:
            line["CPU_RELJOB"].color = theme["warning"]
        elif float(line["CPU_RELJOB"]) < 0.95:
            line["CPU_RELJOB"].color = theme["low"]

        # highlight 'scores'
        if float(line["MEM_RELJOB"]) > 0.9:
            line["MEM_RELJOB"].color = theme["warning"]

    return lines


def read_interpret(data=None, theme=colors()):
    r"""
    Read and interpret ``sinfo -o "%all"``.

    :returns:

        **lines** (``<list<dict>>``)
            A list of dictionaries, that contain the different fields. All data are
            ``GooseSLURM.rich.String`` or derived types.
    """

    return interpret(read(data), theme)
