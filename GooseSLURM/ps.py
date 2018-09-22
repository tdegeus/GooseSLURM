
from . import rich

# ==================================================================================================

def colors(theme=None):
  r'''
Return dictionary of colors.

.. code-block:: python

  {
    'selection' : '...',
  }

:options:

  **theme** ([``'dark'``] | ``<str>``)
    Select color-theme.
  '''

  if theme == 'dark':
    return \
      {
        'selection' : '1;32;40',
      }

  return \
  {
  'selection' : '',
  }

# ==================================================================================================

def read(data=None):
  r'''
Read ``ps -eo pid,user,rss,%cpu,command``.

:options:

  **data** (``<str>``)
    For debugging: specify the output of ``ps -eo pid,user,rss,%cpu,command`` as string.

:returns:

  **lines** ``<list<dict>>``
    A list of dictionaries, that contain the different fields. All data are strings.
  '''

  import subprocess

  # get live info
  if data is None:
    data = subprocess.check_output('ps -eo pid,user,rss,%cpu,command',shell=True).decode('utf-8')

  # extract the header and the info
  header,data = data.split('\n',1)
  data        = list(filter(None,data  .split('\n')))
  header      = list(filter(None,header.split(' ')))

  # convert to list of dictionaries
  # - initialize
  lines = []
  # - loop over lines
  for line in data:
    # -- decode line with information
    d        = ['' for i in header]
    line      = line.strip()
    d[0],line = line.split(' ',1)
    line      = line.strip()
    d[1],line = line.split(' ',1)
    line      = line.strip()
    d[2],line = line.split(' ',1)
    line      = line.strip()
    d[3],line = line.split(' ',1)
    d[4]     = line.strip()
    # -- initialize empty dictionary
    info = {}
    # -- fill dictionary
    for key,val in zip(header,d):
      info[key] = val
    # -- store to list of lines
    lines += [info]

  # return output
  return lines

# ==================================================================================================

def interpret(lines, theme=colors()):
  r'''
Interpret the output of ``GooseSLURM.ps.read``. All fields are converted to the
``GooseSLURM.rich`` classes adding useful colors in the process.

:arguments:

  **lines** ``<list<dict>>``
    The output of ``GooseSLURM.ps.read``

:options:

  **theme** (``<dict>``)
    The color-theme, as selected by ``GooseSLURM.ps.colors``.

:returns:

  **lines** (``<list<dict>>``)
    A list of dictionaries, that contain the different fields. All data are
    ``GooseSLURM.rich.String`` or derived types.
  '''

  # interpret input as list
  if type(lines) != list: lines = [lines]

  # loop over all lines
  for line in lines:

    # custom conversion
    for key in ['%CPU']:
      line[key] = rich.Float(line[key], precision=2)

    # custom conversion
    for key in ['RSS']:
      line[key] = rich.Memory(line[key], default_unit=1e3)

    # convert remaining fields to string
    for key in line:
      if not isinstance(line[key], rich.String):
        line[key] = rich.String(line[key])

  return lines

# ==================================================================================================

def read_interpret(data=None, theme=colors()):
  r'''
Read and interpret ``ps -eo pid,user,rss,%cpu,command``.

:returns:

  **lines** (``<list<dict>>``)
    A list of dictionaries, that contain the different fields. All data are
    ``GooseSLURM.rich.String`` or derived types.
  '''

  return interpret(read(data),theme)

# ==================================================================================================
