import functools
import operator
import os

import click
import yaml


def ContinueDump(filename):
    r"""
    Check to proceed dumping a file
    (checks to create the directory and/or to overwrite an existing file).
    Return ``True`` is the user confirms to proceed.
    """

    dirname = os.path.dirname(filename)

    if os.path.isfile(filename):
        if not click.confirm(f'Overwrite "{filename:s}"?'):
            return False

    elif not os.path.isdir(dirname) and len(dirname) > 0:
        if not click.confirm(f'Create "{os.path.dirname(filename):s}"?'):
            return False

    return True


def YamlRead(filename):
    r"""
    Read YAML file and return its content as ``list`` or ``dict``.
    """

    if not os.path.isfile(filename):
        raise OSError(f'"{filename:s} does not exist')

    with open(filename) as file:
        return yaml.load(file.read(), Loader=yaml.FullLoader)


def YamlGetItem(filename, key=[]):
    r"""
    Get an item from a YAML file.
    Optionally the key to the item can be specified as a list. E.g.
    *   ``[]`` for a YAML file containing only a list.
    *   ``['foo']`` for a plain YAML file.
    *   ``['key', 'to', foo']`` for a YAML file with nested items.
    """

    data = YamlRead(filename)

    if len(key) == 0 and not isinstance(data, list):
        raise OSError(f'Specify key for "{filename:s}"')

    if len(key) > 0:
        try:
            return functools.reduce(operator.getitem, key, data)
        except BaseException:
            raise OSError('"{:s}" not in "{:s}"'.format("/".join(key), filename))

    return data


def YamlDump(filename, data):
    r"""
    Dump data (as ``list`` or ``dict``) to YAML file.
    Unless ``force = True`` the function prompts before overwriting an existing file.
    """

    dirname = os.path.dirname(filename)

    if not os.path.isdir(dirname) and len(dirname) > 0:
        os.makedirs(os.path.dirname(filename))

    with open(filename, "w") as file:
        yaml.dump(data, file)
