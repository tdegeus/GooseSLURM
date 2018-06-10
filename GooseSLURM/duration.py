
import re

# ==================================================================================================

def asSeconds(data):
  r'''
Convert string to seconds, from:

*   A humanly readable time (e.g. "1d").
*   A SLURM time string (e.g. "1-00:00:00").
*   A time string (e.g. "24:00:00").
*   ``int`` or ``float``: interpreted as seconds.
  '''

  if type(data) == int: return data

  if type(data) == float: return int(data)

  if re.match(r'^[0-9]*\-[0-9]*\:[0-9]*\:[0-9]*$', data):

    # - initialize number of days, hours, minutes, seconds
    t  = [0,0,0,0]
    # - split days
    if len(data.split('-')) > 1: t[0],data = data.split('-')
    # - split hours:minutes:seconds (all optional)
    data = data.split(':')
    # - fill from seconds -> minutes (if present) -> hours (if present)
    for i in range(len(data)): t[-1*(i+1)] = data[-1*(i+1)]
    # - return seconds
    return int(t[0])*24*60*60+int(t[1])*60*60+int(t[2])*60+int(t[3])

  if re.match(r'^[0-9]*\:[0-9]*\:[0-9]*$', data):

    # - initialize number of days, hours, minutes, seconds
    t  = [0,0,0]
    # - split hours:minutes:seconds (all optional)
    data = data.split(':')
    # - fill from seconds -> minutes (if present) -> hours (if present)
    for i in range(len(data)): t[-1*i] = data[-1*i]
    # - return seconds
    return int(t[0])*60*60+int(t[1])*60+int(t[2])

  if re.match(r'^[0-9]*\.?[0-9]*[a-zA-Z]$', data):

    # convert input to seconds
    if   data[-1] == 'd': return int( float(data[:-1]) * float(60*60*24) )
    elif data[-1] == 'h': return int( float(data[:-1]) * float(60*60)    )
    elif data[-1] == 'm': return int( float(data[:-1]) * float(60)       )
    elif data[-1] == 's': return int( float(data[:-1]) * float(1)        )

  try:

    return int(data)

  except:

    return None

# ==================================================================================================

def asUnit(data,unit,precision):
  r'''
Convert to string that has a unit, either with a certain precision, or with a default precision.
  '''

  if precision:
    return '{{0:.{precision:d}f}}{{1:s}}'.format(precision=precision).format(data,unit)
  else:
    if abs(round(data)) < 10.: return '{0:.1f}{1:s}'.format(      data ,unit)
    else                     : return '{0:.0f}{1:s}'.format(round(data),unit)

# ==================================================================================================

def asHuman(data,precision=None):
  r'''
Return humanly-readable string.
  '''

  data = asSeconds(data)

  if data is None: return ''

  base = [60*60*24, 60*60, 60, 1]
  name = ['d', 'h', 'm', 's']

  for i,unit in zip(base,name):
    if abs(data) >= i:
      return asUnit(float(data)/float(i), unit, precision)

  return asUnit(float(data), 's', precision)

# ==================================================================================================

def asSlurm(data):
  r'''
Convert to a SLURM time string (e.g. "1-00:00:00").

The input is converted to seconds by ``GooseSLURM.tine.asSeconds()``.
  '''

  data = asSeconds(data)

  if not data: return ''

  s = int( data % 60 );  data = ( data - s ) / 60
  m = int( data % 60 );  data = ( data - m ) / 60
  h = int( data % 24 );  data = ( data - h ) / 24
  d = int( data      )

  return '%d-%02d:%02d:%02d' % (d,h,m,s)

# ==================================================================================================
