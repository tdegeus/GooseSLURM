
import re

# ==================================================================================================

def asBytes(txt):
  r'''
Convert string to bytes, from:

*   A humanly readable string (e.g. "1G").
*   ``int`` or ``float``: interpreted as bytes.
  '''

  if type(txt) == int: return txt

  if type(txt) == float: return int(txt)

  if re.match(r'^[0-9]*\.?[0-9]*[a-zA-Z]$', txt):

    if txt[-1] == 'T': return int( float(txt[:-1]) * 1.e12 )
    if txt[-1] == 'G': return int( float(txt[:-1]) * 1.e9  )
    if txt[-1] == 'M': return int( float(txt[:-1]) * 1.e6  )
    if txt[-1] == 'K': return int( float(txt[:-1]) * 1.e3  )

  try:

    return int(txt)

  except:

    return None

# ==================================================================================================

def asSlurm(byte):
  r'''
Convert to a SLURM string (e.g. "1G").

The input is converted to seconds by ``GooseSLURM.tine.asBytes()``.
  '''

  byte = asBytes(byte)

  if not byte: return None

  if byte % 1e12 == 0: return str(int(byte/1e12)) + 'T'
  if byte % 1e9  == 0: return str(int(byte/1e9 )) + 'G'
  if byte % 1e6  == 0: return str(int(byte/1e6 )) + 'M'
  if byte % 1e3  == 0: return str(int(byte/1e3 )) + 'K'

  return str(byte)

# ==================================================================================================
