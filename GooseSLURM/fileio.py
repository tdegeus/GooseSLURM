import yaml
import os
import operator
import functools
import click


def ContinueDump(filename):
    r'''
Check to proceed dumping a file
(checks to create the directory and/or to overwrite an existing file).
Return ``True`` is the user confirms to proceed.
    '''

    dirname = os.path.dirname(filename)

    if os.path.isfile(filename):
        if not click.confirm('Overwrite "{0:s}"?'.format(filename)):
            return False

    elif not os.path.isdir(dirname) and len(dirname) > 0:
        if not click.confirm('Create "{0:s}"?'.format(os.path.dirname(filename))):
            return False

    return True


def YamlRead(filename):
    r'''
Read YAML file and return its content as ``list`` or ``dict``.
    '''

    if not os.path.isfile(filename):
        raise IOError('"{0:s} does not exist'.format(filename))

    with open(filename, 'r') as file:
        return yaml.load(file.read(), Loader=yaml.FullLoader)


def YamlGetItem(filename, key=[]):
    r'''
Get an item from a YAML file.
Optionally the key to the item can be specified as a list. E.g.
*   ``[]`` for a YAML file containing only a list.
*   ``['foo']`` for a plain YAML file.
*   ``['key', 'to', foo']`` for a YAML file with nested items.
    '''

    data = YamlRead(filename)

    if len(key) == 0 and not isinstance(data, list):
        raise IOError('Specify key for "{0:s}"'.format(filename))

    if len(key) > 0:
        try:
            return functools.reduce(operator.getitem, key, data)
        except BaseException:
            raise IOError('"{0:s}" not in "{1:s}"'.format('/'.join(key), filename))

    return data


def YamlDump(filename, data):
    r'''
Dump data (as ``list`` or ``dict``) to YAML file.
Unless ``force = True`` the function prompts before overwriting an existing file.
    '''

    dirname = os.path.dirname(filename)

    if not os.path.isdir(dirname) and len(dirname) > 0:
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w') as file:
        ret = yaml.dump(data, file)
