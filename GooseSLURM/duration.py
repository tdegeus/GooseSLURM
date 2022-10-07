import re


def asSeconds(data, default=None):
    r"""
    Convert string to seconds. The following input is accepted:

    *   A humanly readable time (e.g. "1d").
    *   A SLURM time string (e.g. "1-00:00:00").
    *   A time string (e.g. "24:00:00").
    *   ``int`` or ``float``: interpreted as seconds.

    :arguments:

        **data** (``<str>`` | ``<float>`` | ``<int>``)
            The input string
            (number are equally accepted; they are directly interpreted as seconds).

    :options:

        **default** ([``None``] | ``<int>``)
            Value to return if the conversion fails.

    :returns:

        ``<int>``
            Number of seconds as integer (or default value if the conversion fails).
    """

    # convert int -> int (implicitly assume that the input is in seconds)
    if isinstance(data, int):
        return data

    # convert float -> float (implicitly assume that the input is in seconds)
    if isinstance(data, float):
        return int(data)

    # convert SLURM time string (e.g. "1-00:00:00")
    if re.match(r"^[0-9]*\-[0-9]*\:[0-9]*\:[0-9]*$", data):

        # - initialize number of days, hours, minutes, seconds
        t = [0, 0, 0, 0]
        # - split days
        if len(data.split("-")) > 1:
            t[0], data = data.split("-")
        # - split hours:minutes:seconds (all optional)
        data = data.split(":")
        # - fill from seconds -> minutes (if present) -> hours (if present)
        for i in range(len(data)):
            t[-1 * (i + 1)] = data[-1 * (i + 1)]
        # - return seconds
        return int(t[0]) * 24 * 60 * 60 + int(t[1]) * 60 * 60 + int(t[2]) * 60 + int(t[3])

    # convert time string in hours (e.g. "24:00:00")
    if re.match(r"^[0-9]*\:[0-9]*\:[0-9]*$", data):

        # - initialize number of hours, minutes, seconds
        t = [0, 0, 0]
        # - split hours:minutes:seconds (all optional)
        data = data.split(":")
        # - fill from seconds -> minutes (if present) -> hours (if present)
        for i in range(len(data)):
            t[-1 * i] = data[-1 * i]
        # - return seconds
        return int(t[0]) * 60 * 60 + int(t[1]) * 60 + int(t[2])

    # convert time string in minutes (e.g. "12:34")
    if re.match(r"^[0-9]*\:[0-9]*$", data):

        # - initialize number of minutes, seconds
        t = [0, 0]
        # - split hours:minutes:seconds (all optional)
        data = data.split(":")
        # - fill from seconds -> minutes (if present) -> hours (if present)
        for i in range(len(data)):
            t[-1 * i] = data[-1 * i]
        # - return seconds
        return int(t[0]) * 60 + int(t[1])

    # convert humanly readable time (e.g. "1d")
    if re.match(r"^[0-9]*\.?[0-9]*[a-zA-Z]$", data):

        if data[-1] == "d":
            return int(float(data[:-1]) * float(60 * 60 * 24))
        elif data[-1] == "h":
            return int(float(data[:-1]) * float(60 * 60))
        elif data[-1] == "m":
            return int(float(data[:-1]) * float(60))
        elif data[-1] == "s":
            return int(float(data[:-1]) * float(1))
        elif data[-1] == "w":
            return int(float(data[:-1]) * float(60 * 60 * 24 * 7))
        elif data[-1] == "M":
            return int(float(data[:-1]) * float(60 * 60 * 24 * 7 * 31))
        elif data[-1] == "y":
            return int(float(data[:-1]) * float(60 * 60 * 24 * 7 * 365))

    # one last try (implicitly assume that the input is in seconds)
    try:
        return int(data)
    except BaseException:
        pass

    # all conversions failed: return default value
    return default


def asUnit(data, unit, precision):
    r"""
    Convert to rich-string with a certain unit and precision. The output is e.g. ``"1.1d"``.

    :arguments:

        **data** (``<int>`` | ``<float>``)
            Numerical value (e.g. ``1.1``).

        **unit** (``<str>``)
            The unit (e.g. ``"d"``).

        **precision** (``<int>``)
            The precision with which to print (e.g. ``1``).

    :returns:

        ``<str>``
            The rich-string.
    """

    if precision:
        return f"{{0:.{precision:d}f}}{{1:s}}".format(data, unit)

    if abs(round(data)) < 10.0:
        return f"{data:.1f}{unit:s}"
    else:
        return f"{round(data):.0f}{unit:s}"


def asHuman(data, precision=None):
    r"""
    Convert to string that has the biggest possible unit.
    For example: ``100`` (seconds) -> ``"1.7m"``.

    :arguments:

        **data** (``<str>`` | ``<float>`` | ``<int>``)
            A time, see ``GooseSLURM.duration.asSeconds`` for conversion.

        **precision** (``<int>``)
            The precision with which to print. By default a precision of one is used for
            ``0 < value < 10``,
            while a precision of zero is used otherwise.

    :returns:

        ``<str>``
            The rich-string.
    """

    data = asSeconds(data)

    if data is None:
        return ""

    units = (
        (24 * 60 * 60, "d"),
        (60 * 60, "h"),
        (60, "m"),
        (1, "s"),
    )

    for val, unit in units:
        if abs(data) >= val:
            return asUnit(float(data) / float(val), unit, precision)

    return asUnit(float(data), "s", precision)


def asSlurm(data):
    r"""
    Convert to a SLURM time string. For example ``"1d"`` -> ``"1-00:00:00"``.

    :arguments:

        **data** (``<str>`` | ``<float>`` | ``<int>``)
            A time, see ``GooseSLURM.duration.asSeconds`` for conversion.

    :returns:

        ``<str>``
            The rich-string.
    """

    data = asSeconds(data)

    if data is None:
        return ""

    s = int(data % 60)
    data = (data - s) / 60
    m = int(data % 60)
    data = (data - m) / 60
    h = int(data % 24)
    data = (data - h) / 24
    d = int(data)

    return "%d-%02d:%02d:%02d" % (d, h, m, s)
