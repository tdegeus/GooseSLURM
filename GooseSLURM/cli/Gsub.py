#!/usr/bin/env python3
'''Gsub
    Submit job-scripts from their directory.

Usage:
    Gsub [options] <files>...

Arguments:
    Job-scripts

Options:
        --dry-run   Print commands to screen, without executing.
        --verbose   Verbose all commands and their output.
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

from .. import __version__

def run(cmd, verbose=False, dry_run=False):

    if dry_run:
        print(cmd)
        return None

    out = subprocess.check_output(cmd, shell=True).decode('utf-8')

    if verbose:
        print(cmd)
        print(out,end='')

    return out


def main():

    # parse command-line options
    args = docopt.docopt(__doc__, version=__version__)

    # check arguments
    for file in args['<files>']:
        if not os.path.isfile(file):
            print('"%s" does not exist' % file)
            return 1

    # submit
    pbar = tqdm.tqdm(args['<files>'], disable=args['--quiet'])

    for file in pbar:

        pbar.set_description(file)

        path, name = os.path.split(file)

        if len(path) > 0:
            cmd = 'cd {0:s}; sbatch {1:s}'.format(path, name)
        else:
            cmd = 'sbatch {0:s}'.format(name)

        run(cmd, verbose=args['--verbose'], dry_run=args['--dry-run'])

        time.sleep(float(args['--wait']))
