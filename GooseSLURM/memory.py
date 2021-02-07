
import re


def asBytes(data, default=None, default_unit=1):
    r'''
Convert string to bytes. The following input is accepted:

*   A humanly readable string (e.g. "1G").
*   ``int`` or ``float``: interpreted as bytes.

:arguments:

    **data** (``<str>`` | ``<float>`` | ``<int>``)
        The input string (number are equally accepted; they are directly interpreted as bytes).

:options:

    **default** ([``None``] | ``<int>``)
        Value to return if the conversion fails.

    **default_unit** (``int``)
        The unit to assume if no unit if specified (specify the number of bytes).

:returns:

    ``<int>``
        Number of bytes as integer (or default value if the conversion fails).
    '''

    # convert int -> int (assume that the unit)
    if isinstance(data, int):
        return data * int(default_unit)

    # convert float -> float (assume that the unit)
    if isinstance(data, float):
        return int(data * default_unit)

    # convert humanly readable time (e.g. "1G")
    if re.match(r'^[0-9]*\.?[0-9]*[a-zA-Z]$', data):

        if data[-1] == 'T':
            return int(float(data[:-1]) * 1.e12)
        if data[-1] == 'G':
            return int(float(data[:-1]) * 1.e9)
        if data[-1] == 'M':
            return int(float(data[:-1]) * 1.e6)
        if data[-1] == 'K':
            return int(float(data[:-1]) * 1.e3)

    # one last try (assume that the unit)
    try:
        return int(float(data) * default_unit)
    except BaseException:
        pass

    # all conversions failed: return default value
    return default


def asUnit(data, unit, precision):
    r'''
Convert to rich-string with a certain unit and precision. The output is e.g. ``"1.1G"``.

:arguments:

    **data** (``<int>`` | ``<float>``)
        Numerical value (e.g. ``1.1``).

    **unit** (``<str>``)
        The unit (e.g. ``"G"``).

    **precision** (``<int>``)
        The precision with which to print (e.g. ``1``).

:returns:

    ``<str>``
        The rich-string.
    '''

    if precision:
        return '{{0:.{precision:d}f}}{{1:s}}'.format(precision=precision).format(data, unit)

    if abs(round(data)) < 10.:
        return '{0:.1f}{1:s}'.format(data, unit)
    else:
        return '{0:.0f}{1:s}'.format(round(data), unit)


def asHuman(data, precision=None):
    r'''
Convert to string that has the biggest possible unit. For example ``1e6`` (bytes) -> ``"1.0M"``.

:arguments:

    **data** (``<str>`` | ``<float>`` | ``<int>``)
        An amount of memory, see ``GooseSLURM.duration.asBytes`` for conversion.

    **precision** (``<int>``)
        The precision with which to print. By default a precision of one is used for
        ``0 < value < 10``,
        while a precision of zero is used otherwise.

:returns:

    ``<str>``
        The rich-string.
    '''

    data = asBytes(data)

    if data is None:
        return ''

    units = (
        (1e12, 'T'),
        (1e9, 'G'),
        (1e6, 'M'),
        (1e3, 'K'),
        (1, 'B'),
    )

    for val, unit in units:
        if abs(data) >= val:
            return asUnit(float(data) / float(val), unit, precision)

    return asUnit(float(data), 'B', precision)


def asSlurm(data):
    r'''
Convert to a SLURM string. For example ``"1G"``.

:arguments:

    **data** (``<str>`` | ``<float>`` | ``<int>``)
        An amount of memory, see ``GooseSLURM.duration.asBytes`` for conversion.

:returns:

    ``<str>``
        The rich-string.
    '''

    data = asBytes(data)

    if data is None:
        return ''

    if data % 1e12 == 0:
        return str(int(data / 1e12)) + 'T'
    if data % 1e9 == 0:
        return str(int(data / 1e9)) + 'G'
    if data % 1e6 == 0:
        return str(int(data / 1e6)) + 'M'
    if data % 1e3 == 0:
        return str(int(data / 1e3)) + 'K'

    return str(data)
