#!/usr/bin/env python3
'''Ginfo
  Summarize the status of the compute nodes (wrapper around "sinfo").

  The following scores are computed of each node:

  * CPU% : the CPU load of the node, relative to the number of jobs.
           cpu_load / cpu_used
           should always be ~1, anything else usually signals misuse

  * Mem% : the amount of used memory, relative to the average memory available per job.
           ( mem_used / cpu_used ) / ( mem_tot / cpu_tot )
           >1 for (several) heavy memory consumption jobs, but in principle any value is possible

Usage:
  Ginfo [options]
  Ginfo [options] [--jobid=N...] [--host=N...] [--user=N...] [--cfree=N...] [--partition=N...] [--sort=N...] [--output=N...] [--debug=N...]

Options:
  -U                      Limit output to the current user.
  -u, --user=<NAME>       Limit output to user(s)      (may be a regex).
  -j, --jobid=<NAME>      Limit output to job-id(s)    (may be a regex).
  -h, --host=<NAME>       Limit output to host(s)      (may be a regex).
  -f, --cfree=<NAME>      Limit output to free CPU(s)  (may be a regex).
  -p, --partition=<NAME>  Limit output to partition(s) (may be a regex).
  -s, --sort=<NAME>       Sort by field (selected by the header name).
  -r, --reverse           Reverse sort.
  -o, --output=<NAME>     Select output columns (selected by the header name).
  -S, --summary           Print only summary.
      --no-header         Suppress header.
      --no-truncate       Print full columns, do not truncate based on screen width.
      --width=<N>         Set print with.
      --colors=<NAME>     Select color scheme from: none, dark. [default: dark]
  -l, --list              Print selected column as list.
      --sep=<NAME>        Set column separator. [default:  ] (space)
      --long              Print full information (each column is printed as a line).
      --debug=<FILE>      Debug: read 'sinfo -o "%all"' (and then squeue) from file.
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
import pkg_resources

__version__ = pkg_resources.require("GooseSLURM")[0].version

from .. import rich
from .. import sinfo
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

  # conversion map: default field-names -> custom field-names
  alias = {
    'HOSTNAMES'  : 'Host',
    'CPUS_T'     : 'CPUs',
    'CPUS_I'     : 'Cfree',
    'CPUS_D'     : 'Cdown',
    'CPUS_O'     : 'Con',
    'CPU_RELJOB' : 'CPU%',
    'PARTITION'  : 'Partition',
    'MEMORY'     : 'Mem',
    'FREE_MEM'   : 'Mfree',
    'MEM_RELJOB' : 'Mem%',
    'TIMELIMIT'  : 'Tlim',
    'STATE'      : 'State',
  }

  # conversion map: custom field-names -> default field-names
  aliasInv = {alias[key].upper():key for key in alias}

  # rename command line options -> default field-names
  for key in [key for key in args]:
    if key.upper() in aliasInv:
      args[aliasInv[key.upper()]] = args.pop(key)

  # print settings of all columns
  # - "width"   : minimum width, adapted to print width (min_width <= width <= real_width)
  # - "align"   : alignment of the columns (except the header)
  # - "priority": priority of column expansing, columns marked "True" are expanded first
  columns = [
    {'key':'HOSTNAMES' ,'width':4, 'align':'<', 'priority':True },
    {'key':'CPUS_T'    ,'width':4, 'align':'>', 'priority':True },
    {'key':'CPUS_I'    ,'width':5, 'align':'>', 'priority':True },
    {'key':'CPU_RELJOB','width':4, 'align':'>', 'priority':True },
    {'key':'MEMORY'    ,'width':3, 'align':'>', 'priority':True },
    {'key':'FREE_MEM'  ,'width':5, 'align':'>', 'priority':True },
    {'key':'MEM_RELJOB','width':4, 'align':'>', 'priority':True },
    {'key':'PARTITION' ,'width':9, 'align':'<', 'priority':True },
    {'key':'TIMELIMIT' ,'width':4, 'align':'>', 'priority':False},
    {'key':'STATE'     ,'width':5, 'align':'<', 'priority':False},
  ]

  # header
  header = {column['key']: rich.String(alias[column['key']],align=column['align'])
    for column in columns}

  # print settings for the summary
  columns_summary = [
    {'key':'PARTITION' ,'width':9, 'align':'<', 'priority':True },
    {'key':'CPUS_T'    ,'width':4, 'align':'>', 'priority':True },
    {'key':'CPUS_O'    ,'width':5, 'align':'>', 'priority':True },
    {'key':'CPUS_D'    ,'width':5, 'align':'>', 'priority':True },
    {'key':'CPUS_I'    ,'width':5, 'align':'>', 'priority':True },
    {'key':'CPU_RELJOB','width':4, 'align':'>', 'priority':True },
    {'key':'MEM_RELJOB','width':4, 'align':'>', 'priority':True },
  ]

  # header
  header_summary = {column['key']: rich.String(alias[column['key']],align=column['align'])
    for column in columns_summary}

  # select color theme
  theme = sinfo.colors(args['colors'].lower())

  # ---------------------------------- load the output of "sinfo" ----------------------------------

  if not args['debug']:

    lines = sinfo.read_interpret(theme=theme)

  else:

    lines = sinfo.read_interpret(
      data  = open(args['debug'][0],'r').read(),
      theme = theme,
    )

  # ----------------------------- limit based on command-line options ------------------------------

  for key in ['HOSTNAMES','PARTITION','CPUS_I']:

    if args[key]:

      # limit data
      lines = [l for l in lines if sum([1 if re.match(n,str(l[key])) else 0 for n in args[key]])]

      # color-highlight selected columns
      # - apply to all remaining lines
      for line in lines: line[key].color = theme['selection']
      # - apply to the header
      header[key].color = theme['selection']

  # --------------------------------- support function used below ----------------------------------

  # if needed, convert 'name[10-14,16]' to 'list(name10, name11, name12, name13, name14, name16)'
  def expand_nodelist(text):

    # try to split 'name', '[10-14]'
    match = list(filter(None, re.split(r'(\[[^\]]*\])', text)))

    # no split made: no need to interpret anything, return as list
    if len(match) == 1: return [text]

    # split in variables
    name, numbers = match

    # remove brackets '[10-14,16]' -> '10-14,16'
    numbers = numbers[1:-1]

    # split '10-14,16' -> list('10-14', '16')
    numbers = numbers.split(',')

    # allocate output
    nodes = []

    # expand if needed
    for number in numbers:

      # '16' -> 'name16'
      if len(number.split('-')) == 1:

        # copy to list
        nodes += [ name + number ]

      # '10-14' -> list('name10', 'name11', 'name12', 'name13', 'name14')
      else:

        # get start and end numbers
        start, end = number.split('-')

        # expand between beginning and end
        nodes += [ name + ('%0'+str(len(start))+'d')%i for i in range(int(start), int(end)+1) ]

    # return output
    return nodes

  # ---------------------------------------- limit to users ----------------------------------------

  # handle 'alias' options
  if args['U']: args['user'] += [pwd.getpwuid(os.getuid())[0]]

  # apply filter
  if args['user'] or args['jobid']:

    import itertools

    # get list of jobs
    # ----------------

    # read
    if not args['debug']:

      jobs = squeue.read_interpret()

    else:

      jobs = squeue.read_interpret(
        data  = open(args['debug'][1],'r').read(),
        now   = os.path.getctime(args['debug'][1]),
      )

    # limit to running jobs
    jobs = [j for j in jobs if str(j['ST'])=='R']

    # limit to users' jobs
    if args['user']:
      jobs = [str(j['NODELIST']) for j in jobs if sum([1 if re.match(n,str(j['USER'])) else 0 for n in args['user']])]

    # limit to specific jobs
    if args['jobid']:
      jobs = [str(j['NODELIST']) for j in jobs if sum([1 if re.match(n,str(j['JOBID'])) else 0 for n in args['jobid']])]

    # get list of nodes for the users' jobs
    # -------------------------------------

    # allocate list of nodes
    nodes = []

    # loop over jobs
    for job in jobs:

      # simple name (e.g. 'f123') -> add to list
      if len(job.split(',')) == 1:
        nodes += expand_nodelist(job)
        continue

      # split all array jobs, e.g.
      # g117,g[123-456],f[023-025] -> ('g117,g', '[123-456]', ',f', '[023-025]')
      match = list(filter(None, re.split(r'(\[[^\]]*\])', job)))

      # loop over arrays
      for name, numbers in zip(match[0::2], match[1::2]):

        # strip plain jobs that are still prepending the array
        name = name.split(',')
        # add plain jobs to node-list
        nodes += name[:-1]
        # interpret all batch jobs and add to node-list
        nodes += expand_nodelist(name[-1]+numbers)

    # filter empty items
    nodes = list(filter(None,nodes))

    # limit data
    lines = [l for l in lines if str(l['HOSTNAMES']) in nodes]

    # color-highlight selected columns
    # - apply to all remaining lines
    for line in lines: line['HOSTNAMES'].color = theme['selection']
    # - apply to the header
    header['HOSTNAMES'].color = theme['selection']

  # --------------------------------------------- sort ---------------------------------------------

  # default sort
  lines.sort(key=lambda line: line['HOSTNAMES'])
  lines.sort(key=lambda line: line['PARTITION'])

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

  # get names of the different partitions
  partitions = sorted(set([str(line['PARTITION']) for line in lines]))

  # start a new list of "node information", summed on the relevant nodes
  partitions = [{'PARTITION':gs.rich.String(key)} for key in partitions]

  # loop over partitions
  for partition in partitions:

    # - isolate nodes for this partition
    N = [line for line in lines if str(line['PARTITION']) == str(partition['PARTITION'])]

    # - get the CPU count
    partition['CPUS_T'] = rich.Integer(sum([int(line['CPUS_T']) for line in N]))
    partition['CPUS_O'] = rich.Integer(sum([int(line['CPUS_O']) for line in N]))
    partition['CPUS_D'] = rich.Integer(sum([int(line['CPUS_D']) for line in N]))
    partition['CPUS_I'] = rich.Integer(sum([int(line['CPUS_I']) for line in N]))

    # - initialize scores
    partition['CPU_RELJOB'] = rich.Float('')
    partition['MEM_RELJOB'] = rich.Float('')

    # - average load
    if len([1 for line in N if line['CPU_RELJOB'].isnumeric()]) > 0:
      partition['CPU_RELJOB'] = rich.Float(
        sum([float(line['CPU_RELJOB']) for line in N if line['CPU_RELJOB'].isnumeric()]) /
        sum([1.                        for line in N if line['CPU_RELJOB'].isnumeric()])
      )

    # - average memory consumption
    if len([1 for line in N if line['MEM_RELJOB'].isnumeric()]) > 0:
      partition['MEM_RELJOB'] = rich.Float(
        sum([float(line['MEM_RELJOB']) for line in N if line['MEM_RELJOB'].isnumeric()]) /
        sum([1.                        for line in N if line['MEM_RELJOB'].isnumeric()])
      )

    # - highlight 'scores'
    if   int  (partition['CPUS_I']    ) > 0   : partition['CPUS_I'    ].color = theme['free'   ]
    if   float(partition['CPU_RELJOB']) > 1.05: partition['CPU_RELJOB'].color = theme['warning']
    elif float(partition['CPU_RELJOB']) < 0.95: partition['CPU_RELJOB'].color = theme['low'    ]

  # rename field
  lines = partitions

  # --------------------------------------------- sort ---------------------------------------------

  # default sort
  lines.sort(key=lambda line: line['PARTITION'], reverse=args['reverse'])

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
