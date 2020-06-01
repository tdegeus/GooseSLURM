'''Ghecksync
    Check which files to copy to get two folders (one optionally remote) in sync.

Usage:
    Ghecksync [options] <source> <dest>

Arguments:
  ID-number(s) of the job(s) to delete. (default: all user's jobs)

Options:
    -s, --source=N  Remote name for source.
    -o, --output=N  Base-name for output file. [default: Gchecksync]
        --iname=N   Find using the "iname" option.
    -h, --help      Show help.
        --version   Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
'''

import docopt
import subprocess

from .. import __version__

def convert_root(root, remote=False):

    cmd

    if remote:
        return filter(None, subprocess.check_output(cmd, shell=True).decode('utf-8'))



def get_files(cmd, root):

    files = sorted(list(filter(None, subprocess.check_output(
        cmd, shell=True).decode('utf-8').split('\n'))))

    ret = {}

    for file in files:
        file = file.replace('  ', ' ')
        _, _, _, _, size, _, _, _, path = file.split(' ')
        path = path.replace(root, '')
        ret[path] = size

    return ret


def main():

    args = docopt.docopt(__doc__, version=__version__)

    if not args['--iname']:
        raise IOError('WIP: implement other search options')









import sys
import os
import re
import subprocess

def get(cmd):

    files = sorted(list(filter(None, subprocess.check_output(
        cmd, shell=True).decode('utf-8').split('\n'))))

    ret = {}

    for file in files:
        file = file.replace('  ', ' ')
        _, _, _, _, size, _, _, _, path = file.split(' ')
        path = '/'.join(path.split('/')[-2:])
        ret[path] = size

    return ret

files_fidis = get("ssh fidis \"find /home/tdegeus/scratch/front_velocity/newdata -iname '*.hdf5' -exec ls -l {} \;\"")
files_local = get("find . -iname '*.hdf5' -exec ls -l {} \;")

def not_exists(source, dest):

    ret = []

    for file in sorted(source):
        if file not in dest:
            ret += [file]

    return ret

def not_same(source, dest):

    ret = []

    for file in sorted(source):
        if file not in dest:
            continue
        if source[file] != dest[file]:
            ret += [file]

    return ret

def as_copy(files):

    ret = []

    for file in files:
        ret += ['scp fidis:/home/tdegeus/scratch/front_velocity/newdata/{0:s} {0:s}'.format(file)]

    return ret

open('not-on-fidis.txt', 'w').write('\n'.join(not_exists(files_local, files_fidis)))
open('not-on-local.txt', 'w').write('\n'.join(as_copy(not_exists(files_fidis, files_local))))
open('different.txt', 'w').write('\n'.join(not_same(files_local, files_fidis)))
