#!/usr/bin/env python3
'''Gsub
    Submit job-scripts from their directory.

Usage:
    Gsub [options] --input=N
    Gsub [options] <files>...

Arguments:
    Job-scripts

Options:
        --dry-run   Print commands to screen, without executing.
        --verbose   Verbose all commands and their output.
    -i, --input=N   Submit files stored in YAML-file.
    -k, --key=N     Path in the YAML-file, separated by "/". [default: /]
    -o, --output=N  Output status to YAML-file.
    -w, --wait=N    Seconds to wait between submitting jobs. [default: 2]
    -q, --quiet     Do no show progress.
    -h, --help      Show help.
        --version   Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
'''

import os
import sys
import re
import subprocess
import docopt
import time
import tqdm
import click

from .. import __version__
from .. import fileio


def run(cmd, verbose=False, dry_run=False):

    if dry_run:
        print(cmd)
        return None

    out = subprocess.check_output(cmd, shell=True).decode('utf-8')

    if verbose:
        print(cmd)
        print(out,end='')

    return out


def dump(files, ifile, outname):

    if not outname:
        return

    data = {
        'submitted': [files[i] for i in range(ifile - 1)]
        'pending': [files[i] for i in range(ifile, len(files))]
    }

    fileio.YamlDump(outname, data, force=True)


def main():

    # parse command-line options
    args = docopt.docopt(__doc__, version=__version__)
    files = args['<files>']

    # checkout existing output
    if args['--output']:
        if os.path.isfile(filename):
            if not click.confirm('Overwrite "{0:s}"?'.format(filename)):
                return 1
        elif not os.path.isdir(dirname) and len(dirname) > 0:
            if not click.confirm('Create "{0:s}"?'.format(os.path.dirname(filename))):
                return 1

    # read YAML-file
    if args['--input']:
        source = args['--input']
        key = list(filter(None, args['--key'].split('/')))
        files = fileio.YamlGetItem(source, key)

    # check arguments
    for file in files:
        if not os.path.isfile(file):
            print('"%s" does not exist' % file)
            return 1

    # submit
    pbar = tqdm.tqdm(files, disable=args['--quiet'])

    for ifile, file in enumerate(pbar):
        pbar.set_description(file)
        path, name = os.path.split(file)

        if len(path) > 0:
            cmd = 'cd {0:s}; sbatch {1:s}'.format(path, name)
        else:
            cmd = 'sbatch {0:s}'.format(name)

        run(cmd, verbose=args['--verbose'], dry_run=args['--dry-run'])
        time.sleep(float(args['--wait']))
        dump(files, ifile, args['--output'])
