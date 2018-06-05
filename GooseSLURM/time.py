
import re

# ==================================================================================================

def asSeconds(txt):
  r'''
Convert string to seconds, from:

*   A humanly readable time (e.g. "1d").
*   A SLURM time string (e.g. "1-00:00:00").
*   A time string (e.g. "24:00:00").
*   ``int`` or ``float``: interpreted as seconds.
  '''

  if type(txt) == int: return txt

  if type(txt) == float: return int(txt)

  if re.match(r'^[0-9]*\-[0-9]*\:[0-9]*\:[0-9]*$', txt):

    # - initialize number of days, hours, minutes, seconds
    t  = [0,0,0,0]
    # - split days
    if len(txt.split('-')) > 1: t[0],txt = txt.split('-')
    # - split hours:minutes:seconds (all optional)
    txt = txt.split(':')
    # - fill from seconds -> minutes (if present) -> hours (if present)
    for i in range(len(txt)): t[-1*(i+1)] = txt[-1*(i+1)]
    # - return seconds
    return int(t[0])*24*60*60+int(t[1])*60*60+int(t[2])*60+int(t[3])

  if re.match(r'^[0-9]*\:[0-9]*\:[0-9]*$', txt):

    # - initialize number of days, hours, minutes, seconds
    t  = [0,0,0]
    # - split hours:minutes:seconds (all optional)
    txt = txt.split(':')
    # - fill from seconds -> minutes (if present) -> hours (if present)
    for i in range(len(txt)): t[-1*i] = txt[-1*i]
    # - return seconds
    return int(t[0])*60*60+int(t[1])*60+int(t[2])

  if re.match(r'^[0-9]*\.?[0-9]*[a-zA-Z]$', txt):

    # convert input to seconds
    if   txt[-1] == 'd': return int( float(txt[:-1]) * float(60*60*24) )
    elif txt[-1] == 'h': return int( float(txt[:-1]) * float(60*60)    )
    elif txt[-1] == 'm': return int( float(txt[:-1]) * float(60)       )
    elif txt[-1] == 's': return int( float(txt[:-1]) * float(1)        )

  try:

    return int(txt)

  except:

    return None

# ==================================================================================================

def asSlurm(sec):
  r'''
Convert to a SLURM time string (e.g. "1-00:00:00").

The input is converted to seconds by ``GooseSLURM.tine.asSeconds()``.
  '''

  sec = asSeconds(sec)

  if not sec: return None

  s = int( sec % 60 );  sec = ( sec - s ) / 60
  m = int( sec % 60 );  sec = ( sec - m ) / 60
  h = int( sec % 24 );  sec = ( sec - h ) / 24
  d = int( sec      )

  return '%d-%02d:%02d:%02d' % (d,h,m,s)

# ==================================================================================================
