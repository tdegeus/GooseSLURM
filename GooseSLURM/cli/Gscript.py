#!/usr/bin/env python3
'''Gscript
    Write a generic job-script.

Usage:
    Gscript [options] <filename>

Options:
    -h, --help      Show help.
        --version   Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
'''

# --------------------------------------------------------------------------------------------------

import docopt

from .. import __version__
from .. import scripts

# --------------------------------------------------------------------------------------------------

def main():

    # parse command-line options
    args = docopt.docopt(__doc__, version=__version__)

    # write a plain job-script
    open(args['<filename>'], 'w').write(scripts.plain())

