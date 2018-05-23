
import re

# ==================================================================================================

def astime(T):
  r'''
Convert humanly readable time as time that can be read by SLURM (e.g. "1d" -> "24:00:00"). Both
input and output should be a string.
  '''

  # check if format is already correct
  if re.match(r'[0-9]*\:[0-9]*\:[0-9]*',T): return T

  # convert input to seconds
  if   T[-1] == 'd': T = float(T[:-1]) * float(60*60*24)
  elif T[-1] == 'h': T = float(T[:-1]) * float(60*60)
  elif T[-1] == 'm': T = float(T[:-1]) * float(60)
  elif T[-1] == 's': T = float(T[:-1]) * float(1)
  else             : T = float(T)

  # convert seconds back to hours:minutes:seconds
  T = int(T)
  s = int( T % 60 );  T = ( T - s ) / 60
  m = int( T % 60 );  T = ( T - m ) / 60
  h = int( T )

  return '%d:%02d:%02d' % (h,m,s)

# ==================================================================================================
