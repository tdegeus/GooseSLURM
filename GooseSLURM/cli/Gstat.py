#!/usr/bin/env python3
'''Gstat
  Summarize the status of the jobs (wrapper around "squeue").

Usage:
  Gstat [options]
  Gstat [options] [--jobid=N...] [--host=N...] [--user=N...] [--name=N...] [--account=N...] [--partition=N...] [--sort=N...] [--output=N...]

Options:
  -U                      Limit output to the current user.
  -u, --user=<NAME>       Limit output to user(s)      (may be a regex).
  -j, --jobid=<NAME>      Limit output to job-id(s)    (may be a regex).
  -h, --host=<NAME>       Limit output to host(s)      (may be a regex).
  -a, --account=<NAME>    Limit output to account(s)   (may be a regex).
  -n, --name=<NAME>       Limit output to job-name(s)  (may be a regex).
      --status=<NAME>     Limit output to status       (may be a regex).
  -p, --partition=<NAME>  Limit output to partition(s) (may be a regex).
  -s, --sort=<NAME>       Sort by field (selected by the header name).
  -r, --reverse           Reverse sort.
  -o, --output=<NAME>     Select output columns (selected by the header name).
      --full-name         Show full user names.
  -S, --summary           Print only summary.
      --no-header         Suppress header.
      --no-truncate       Print full columns, do not truncate based on screen width.
      --width=<N>         Set print with.
      --colors=<NAME>     Select color scheme from: none, dark. [default: dark]
  -l, --list              Print selected column as list.
      --sep=<NAME>        Set column separator. [default:  ] (space)
      --long              Print full information (each column is printed as a line).
      --debug=<FILE>      Debug: read 'squeue -o "%all"' from file.
      --help              Show help.
      --version           Show version.

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/GooseSLURM
'''

# --------------------------------------------------------------------------------------------------

import os
import sys
import re
import subprocess
import docopt
import pwd

from .. import __version__
from .. import rich
from .. import squeue
from .. import table

# --------------------------------------------------------------------------------------------------

def main():

  # --------------------------------- parse command line arguments ---------------------------------

  # parse command-line options
  args = docopt.docopt(__doc__, version=__version__)

  # change keys to simplify implementation:
  # - remove leading "-" and "--" from options
  args = {re.sub(r'([\-]{1,2})(.*)',r'\2',key): args[key] for key in args}
  # - change "-" to "_" to facilitate direct use in print format
  args = {key.replace('-','_'): args[key] for key in args}

  # -------------------------------- field-names and print settings --------------------------------

  # handle 'alias' options
  if args['U']: args['user'] += [pwd.getpwuid(os.getuid())[0]]

  # conversion map: default field-names -> custom field-names
  alias = {
    'JOBID'           :'JobID'    ,
    'USER'            :'User'     ,
    'ACCOUNT'         :'Account'  ,
    'NAME'            :'Name'     ,
    'START_TIME'      :'Tstart'   ,
    'TIME_LEFT'       :'Tleft'    ,
    'NODES'           :'#node'    ,
    'CPUS'            :'#CPU'     ,
    'CPUS_R'          :'#CPU(R)'  ,
    'CPUS_PD'         :'#CPU(PD)' ,
    'MIN_MEMORY'      :'MEM'      ,
    'ST'              :'ST'       ,
    'NODELIST(REASON)':'Host'     ,
    'PARTITION'       :'Partition',
  }

  # conversion map: custom field-names -> default field-names
  aliasInv = {alias[key].upper():key for key in alias}

  # rename command line options -> default field-names
  # - add key-names
  aliasInv['STATUS'] = 'ST'
  # - apply conversion
  for key in [key for key in args]:
    if key.upper() in aliasInv:
      args[aliasInv[key.upper()]] = args.pop(key)

  # print settings of all columns
  # - "width"   : minimum width, adapted to print width (min_width <= width <= real_width)
  # - "align"   : alignment of the columns (except the header)
  # - "priority": priority of column expansing, columns marked "True" are expanded first
  columns = [
    {'key':'JOBID'           , 'width':7 , 'align':'>', 'priority': True },
    {'key':'USER'            , 'width':7 , 'align':'<', 'priority': True },
    {'key':'ACCOUNT'         , 'width':7 , 'align':'<', 'priority': True },
    {'key':'NAME'            , 'width':11, 'align':'<', 'priority': False},
    {'key':'START_TIME'      , 'width':6 , 'align':'>', 'priority': True },
    {'key':'TIME_LEFT'       , 'width':5 , 'align':'>', 'priority': True },
    {'key':'NODES'           , 'width':5 , 'align':'>', 'priority': True },
    {'key':'CPUS'            , 'width':4 , 'align':'>', 'priority': True },
    {'key':'MIN_MEMORY'      , 'width':3 , 'align':'>', 'priority': True },
    {'key':'ST'              , 'width':2 , 'align':'<', 'priority': True },
    {'key':'PARTITION'       , 'width':9 , 'align':'<', 'priority': False},
    {'key':'NODELIST(REASON)', 'width':5 , 'align':'<', 'priority': False},
  ]

  # header
  header = {column['key']: rich.String(alias[column['key']],align=column['align'])
    for column in columns}

  # print settings for the summary
  columns_summary = [
    {'key':'USER'            , 'width':7 , 'align':'<', 'priority': True },
    {'key':'ACCOUNT'         , 'width':7 , 'align':'<', 'priority': False},
    {'key':'CPUS'            , 'width':4 , 'align':'>', 'priority': True },
    {'key':'CPUS_R'          , 'width':6 , 'align':'>', 'priority': True },
    {'key':'CPUS_PD'         , 'width':6 , 'align':'>', 'priority': True },
    {'key':'PARTITION'       , 'width':9 , 'align':'<', 'priority': False},
  ]

  # header
  header_summary = {column['key']: rich.String(alias[column['key']],align=column['align'])
    for column in columns_summary}

  # select color theme
  theme = squeue.colors(args['colors'].lower())

  # --------------------------------- load the output of "squeue" ----------------------------------

  if not args['debug']:

    lines = squeue.read_interpret(theme=theme)

  else:

    lines = squeue.read_interpret(
      data  = open(args['debug'],'r').read(),
      now   = os.path.getctime(args['debug']),
      theme = theme,
    )

  # ----------------------------- limit based on command-line options ------------------------------

  for key in ['USER','ACCOUNT','NAME','JOBID','ST','NODELIST(REASON)','PARTITION']:

    if args[key]:

      # limit data
      lines = [l for l in lines if sum([1 if re.match(n,str(l[key])) else 0 for n in args[key]])]

      # color-highlight selected columns
      # - apply to all remaining lines
      for line in lines: line[key].color = theme['selection']
      # - apply to the header
      header[key].color = theme['selection']

  # --------------------------------------------- sort ---------------------------------------------

  # default sort
  lines.sort(key=lambda line: line['START_TIME'], reverse=not args['reverse'])

  # optional: sort by key(s)
  if args['sort']:

    for key in args['sort']:

      lines.sort(key=lambda line: line[aliasInv[key.upper()]], reverse=args['reverse'])

  # ---------------------------------------- select columns ----------------------------------------

  if args['output']:

    keys = [aliasInv[key.upper()] for key in args['output']]

    columns = [column for column in columns if column['key'] in keys]

  # -------------------------------------------- print ---------------------------------------------

  if not args['summary']:

    # optional: print all fields and quit
    if args['long']:

      table.print_long(lines)

      sys.exit(0)

    # optional: print as list and quit
    elif args['list']:

      # - only one field can be selected
      if len(columns) > 1:
        print('Only one field can be selected')
        sys.exit(1)

      # - print and quit
      table.print_list(lines, columns[0]['key'], args['sep'])

      sys.exit(0)

    # default: print columns
    else:

      table.print_columns(lines, columns, header, args['no_truncate'], args['sep'], args['width'])

      sys.exit(0)

  # ------------------------------------ summarize information -------------------------------------

  # get names of the different users
  users = sorted(set([str(line['USER']) for line in lines]))

  # start a new list of "user information", summed on the relevant users
  users = [{'USER':gs.rich.String(key)} for key in users]

  # loop over users
  for user in users:

    # - isolate jobs for this user
    N = [line for line in lines if str(line['USER']) == str(user['USER'])]

    # - get (a list of) partition(s)/account(s)
    user['PARTITION'] = rich.String(','.join(list(set([str(line['PARTITION']) for line in N]))))
    user['ACCOUNT'  ] = rich.String(','.join(list(set([str(line['ACCOUNT'  ]) for line in N]))))

    # - count used CPU (per category)
    user['CPUS'   ] = rich.Integer(sum([int(line['CPUS'   ]) for line in N]))
    user['CPUS_R' ] = rich.Integer(sum([int(line['CPUS_R' ]) for line in N]))
    user['CPUS_PD'] = rich.Integer(sum([int(line['CPUS_PD']) for line in N]))

    # - remove zeros from output for more intuitive output
    for key in ['CPUS_R', 'CPUS_PD']:
      if int(user[key]) == 0:
        user[key] = rich.Integer('-')

  # rename field
  lines = users

  # --------------------------------------------- sort ---------------------------------------------

  # default sort
  lines.sort(key=lambda line: line['USER'], reverse=args['reverse'])

  # optional: sort by key(s)
  if args['sort']:

    # get available keys in the setting with fewer columns
    keys = [alias[column['key']].upper() for column in columns_summary]

    # filter sort keys that are not available in this mode
    args['sort'] = [key for key in args['sort'] if key.upper() in keys]

    # apply sort
    for key in args['sort']:
      lines.sort(key=lambda line: line[aliasInv[key.upper()]], reverse=args['reverse'])

  # -------------------------------------------- print ---------------------------------------------

  table.print_columns(lines, columns_summary, header_summary,
    args['no_truncate'], args['sep'], args['width'])
