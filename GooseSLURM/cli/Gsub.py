#!/usr/bin/env python3
'''Gsub
  Submit job-scripts from their directory.

Usage:
  Gsub [options] <FILES>...

Arguments:
  Job-scripts

Options:
      --dry-run   Print commands to screen, without executing.
      --verbose   Verbose all commands and their output.
  -h, --help      Show help.
      --version   Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
'''

# --------------------------------------------------------------------------------------------------

import os
import sys
import re
import subprocess
import docopt

# ----------------------------------- function to fun a command ------------------------------------

def run(cmd,verbose=False,dry_run=False,**kwargs):

  if dry_run:
    print(cmd)
    return None

  out = subprocess.check_output(cmd,shell=True).decode('utf-8')

  if verbose:
    print(cmd)
    print(out,end='')

  return out

# --------------------------------------------------------------------------------------------------

def main():

  # --------------------------------- parse command line arguments ---------------------------------

  # parse command-line options
  args = docopt.docopt(__doc__,version='0.0.6')

  # change keys to simplify implementation:
  # - remove leading "-" and "--" from options
  args = {re.sub(r'([\-]{1,2})(.*)',r'\2',key): args[key] for key in args}
  # - change "-" to "_" to facilitate direct use in print format
  args = {key.replace('-','_'): args[key] for key in args}
  # - remove "<...>"
  args = {re.sub(r'(<)(.*)(>)',r'\2',key): args[key] for key in args}

  # --------------------------------------- check arguments ----------------------------------------

  for file in args['FILES']:

    if not os.path.isfile(file):

      print('"%s" does not exist' % file)

      sys.exit(1)

  # -------------------------------------------- submit --------------------------------------------

  for file in args['FILES']:

    path, name = os.path.split(file)

    if len(path) > 0 : cmd = 'cd %s; sbatch %s' % ( path, name )
    else             : cmd = 'sbatch %s'        % ( name       )

    run(cmd,**args)
