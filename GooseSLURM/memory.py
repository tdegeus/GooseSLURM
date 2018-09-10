
import re

# ==================================================================================================

def asBytes(data, default=None, default_unit=1):
  r'''
Convert string to bytes (``int``), from:

*   A humanly readable string (e.g. "1G").
*   ``int`` or ``float``: interpreted as bytes.

:options:

  **default_unit** (``int``)
    The unit to assume if no unit if specified (specify the number of bytes).
  '''

  if type(data) == int: return data

  if type(data) == float: return int(data)

  if re.match(r'^[0-9]*\.?[0-9]*[a-zA-Z]$', data):

    if data[-1] == 'T': return int( float(data[:-1]) * 1.e12 )
    if data[-1] == 'G': return int( float(data[:-1]) * 1.e9  )
    if data[-1] == 'M': return int( float(data[:-1]) * 1.e6  )
    if data[-1] == 'K': return int( float(data[:-1]) * 1.e3  )

  try:

    return int( float(data) * default_unit )

  except:

    return default

# ==================================================================================================

def asUnit(data,unit,precision):
  r'''
Convert to string with a certain unit and precision.
  '''

  if precision:
    return '{{0:.{precision:d}f}}{{1:s}}'.format(precision=precision).format(data,unit)
  else:
    if abs(round(data)) < 10.: return '{0:.1f}{1:s}'.format(      data ,unit)
    else                     : return '{0:.0f}{1:s}'.format(round(data),unit)

# ==================================================================================================

def asHuman(data,precision=None):
  r'''
Convert to string that has the biggest possible unit (for example hours, or days). Use either the
default precision, or use a default one.
  '''

  data = asBytes(data)

  if data is None: return ''

  base = [1e12, 1e9, 1e6, 1e3, 1]
  name = ['T', 'G', 'M', 'K', 'B']

  for i,unit in zip(base,name):
    if abs(data) >= i:
      return asUnit(float(data)/float(i), unit, precision)

  return asUnit(float(data), 'B', precision)

# ==================================================================================================

def asSlurm(data):
  r'''
Convert to a SLURM string (e.g. "1G").
  '''

  data = asBytes(data)

  if data is None: return ''

  if data % 1e12 == 0: return str(int(data/1e12)) + 'T'
  if data % 1e9  == 0: return str(int(data/1e9 )) + 'G'
  if data % 1e6  == 0: return str(int(data/1e6 )) + 'M'
  if data % 1e3  == 0: return str(int(data/1e3 )) + 'K'

  return str(data)

# ==================================================================================================
