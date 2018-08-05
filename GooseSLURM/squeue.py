
from . import rich

# ==================================================================================================

def colors(theme='dark'):
  r'''
Return named colors:

*   selection
*   queued

:options:

  **theme** ([``'dark'``] | ``<str>``)
    Select color-theme.
  '''

  if theme == 'dark':
    return \
      {
        'selection' : '1;32;40',
        'queued'    : '0;37',
      }

  return \
  {
  'selection' : '',
  'queued'    : '',
  }

# ==================================================================================================

def read(data=None):
  r'''
Read and convert the output of ``squeue -o "%all"`` (or specify its output as a string, for
debugging). The output is a list of dictionaries, with that contain he different output fields. All
data are strings.

Proceed with ``GooseSLURM.squeue.interpret`` for pretty printing.
  '''

  import subprocess

  # get live job-info
  if data is None: data = subprocess.check_output('squeue -o "%all"',shell=True).decode('utf-8')

  # extract the header and the info
  head,data = data.split('\n',1)
  data      = list(filter(None,data.split('\n')))

  # get the field-names
  head = head.split('|')

  # convert name (bug in slurm)
  # Bug #4948, https://bugs.schedmd.com
  idx = [i for i,key in enumerate(head) if key.strip()=='USER']
  if len(idx) > 1:
    head[idx[1]] = 'USER_ID'

  # convert to list of dictionaries
  # - initialize
  lines = []
  # - loop over lines
  for line in data:
    # -- initialize empty dictionary
    info = {}
    # -- fill dictionary
    for key,val in zip(head,line.split('|')):
      if len(key.strip()) > 0:
        info[key.strip()] = val.strip()
    # -- store to list of lines
    lines += [info]

  # return output
  return lines

# ==================================================================================================

def interpret(lines, now=None):
  r'''
Interpret the job info (output of ``GooseSLURM.squeue.read``). All fields are converted to the
``GooseSLURM.rich`` classes adding useful colors in the process.
  '''

  import time

  # read time
  if now is None: now = time.mktime(time.localtime())

  # interpret input as list
  if type(lines) != list: lines = [lines]

  # loop over all lines
  for line in lines:

    # string (-> integer) -> rich.Integer
    for key in ['CPUS','NODES']:
      line[key] = rich.Integer(line[key])

    # "year-month-dayThour:minute:second" (e.g. "2017-11-05T19:09:53") -> seconds from now
    for key in ['START_TIME','SUBMIT_TIME']:
      try:
        line[key] = rich.Duration(int(now-time.mktime(time.strptime(line[key],'%Y-%m-%dT%H:%M:%S'))))
      except:
        line[key] = rich.Duration(line[key])

    # "days-hours:mins:secs" (e.g. "1-4:18:13") -> seconds
    for key in ['TIME_LIMIT','TIME_LEFT','TIME']:
      line[key] = rich.Duration(line[key])

    # convert memory (e.g. "4G") -> bytes
    for key in ['MIN_MEMORY']:
      line[key] = rich.Memory(line[key])

    # specialize number of CPUS
    if str(line['ST']) == 'R':
      line['CPUS_R' ] = rich.Integer(int(line['CPUS']))
      line['CPUS_PD'] = rich.Integer(0)
    else:
      line['CPUS_R' ] = rich.Integer(0)
      line['CPUS_PD'] = rich.Integer(int(line['CPUS']))

    # convert remaining fields to string
    for key in line:
      if not isinstance(line[key], rich.String):
        line[key] = rich.String(line[key])

  return lines

# ==================================================================================================
