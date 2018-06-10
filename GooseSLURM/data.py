
# ==================== CLASS TO REPRESENT A STRING, AND PROVIDE A PRINT FORMAT =====================

class String:
  r'''
To enable printing in columns, optionally with colors, of different variable types, each variable
below is constructed to be a "String" or one of its derived classes:

- String   : represents a string.
- Integer  : represents an integer.
- Float    : represents a float.
- Duration : represents a duration in seconds.
- Memory   : represents memory in bytes.

Arguments (also class-variables which may be modified at any time):

- data      : the data itself, for numeric classes (Integer, Float, Duration, Memory) non-numeric
              strings are retained

Options (also class-variables which may be modified at any time):

- width     : the width for formatted print [default: None]
- color     : the color for formatted print (e.g. "1;32" for bold green) [default: None]
- align     : "<" for left align, ">" for right align [default: "<"]
- precision : floating point precision (only for Float, Duration, Memory) [default: None]
              (None -> automatic precision: Float == 2, Duration == 0/1, Memory == 0)

The classes have the following features:

- format

    Formatted print, applying the set print format.

    This class defines and applies the print format for a string, all numeric classes are converted
    to a string before applying this format, i.e. the precision/unit is applied in the "__str__"
    methods of the respective classes.

- isnumeric

    Return whether the underlying data is numeric or not.

- len(...)

    The length of the unformatted string.

    For the classes Float, Duration, Memory the precision/unit is in the "__str__" methods of the
    respective classes. The length is the length of the result thereof.

- str(...)

    Convert to a string.

    For the classes Float, Duration, Memory this string is formatted to the set precision/unit.

- int(...), float(...)

    Convert to an integer / a float.

    For non-numeric data the function return 0.
  '''

  # ------------------------------------------- __init__ -------------------------------------------

  def __init__(self,data,width=None,align='<',color=None):

    self.data  = data
    self.width = width
    self.color = color
    self.align = align

  # -------------------- return formatted string, align/width/color are applied --------------------

  def format(self):

    if self.width and self.color:
      fmt = '\x1b[{color:s}m{{0:{align:s}{width:d}.{width:d}s}}\x1b[0m'.format(**self.__dict__)
    elif self.width:
      fmt = '{{0:{align:s}{width:d}.{width:d}s}}'.format(**self.__dict__)
    elif self.color:
      fmt = '\x1b[{color:s}m{{0:{align:s}s}}\x1b[0m'.format(**self.__dict__)
    else:
      fmt = '{{0:{align:s}s}}'.format(**self.__dict__)

    return fmt.format(str(self))

  # ------------------------------- return True if "data" is numeric -------------------------------

  def isnumeric(self):

    return False

  # ------- return unformatted string (Float, Duration, Memory: precision/unit are applied) --------

  def __str__(self):

    return str(self.data)

  # ---------------------------------- convert to a dummy integer ----------------------------------

  def __int__(self):

    return 0

  # ----------------------------------- convert to a dummy float -----------------------------------

  def __float__(self):

    return 0.0

  # ------------------------------ length of the result of "__str__" -------------------------------

  def __len__(self):

    return len(str(self))

  # -------------------------------- return the result of "__str__" --------------------------------

  def __repr__(self):

    return str(self)

  # -------------------------------- compare two values as strings ---------------------------------

  def __lt__(self,other):

    return str(self) < str(other)

# ================================= CLASS TO REPRESENT AN INTEGER ==================================

class Integer(String):

  # ------------------------------------------- __init__ -------------------------------------------

  def __init__(self,data,**kwargs):

    try   : data = int(data)
    except: pass

    super().__init__(data,**kwargs)

  # ------------------------------- return True if "data" is numeric -------------------------------

  def isnumeric(self):

    if   type(self.data) == int  : return True
    elif type(self.data) == float: return True
    else                         : return False

  # ---------------------- return numeric value as integer, or return a dummy ----------------------

  def __int__(self):

    if   type(self.data) == int  : return self.data
    elif type(self.data) == float: return int(self.data)
    else                         : return 0

  # ----------------------- return numeric value as float, or return a dummy -----------------------

  def __float__(self):

    if   type(self.data) == int  : return float(self.data)
    elif type(self.data) == float: return self.data
    else                         : return 0.0

  # -------------- compare two numeric values, use fixed rules if one is not numeric ---------------

  def __lt__(self,other):

    if   self .isnumeric() and other.isnumeric(): return int(self) < int(other)
    elif self .isnumeric()                      : return  0
    elif other.isnumeric()                      : return -1
    else                                        : return self.data < other.data

# =================================== CLASS TO REPRESENT A FLOAT ===================================

class Float(String):

  # ------------------------------------------- __init__ -------------------------------------------

  def __init__(self,data,**kwargs):

    try   : data = float(data)
    except: pass

    self.precision = kwargs.pop('precision',2)

    super().__init__(data,**kwargs)

  # ------------------------------- return True if "data" is numeric -------------------------------

  def isnumeric(self):

    if   type(self.data) == float: return True
    elif type(self.data) == int  : return True
    else                         : return False

  # ------------------------- return string, formatted to fixed precision --------------------------

  def __str__(self):

    if not self.isnumeric(): return self.data

    return '{{0:.{precision:d}f}}'.format(**self.__dict__).format(self.data)

  # ---------------------- return numeric value as integer, or return a dummy ----------------------

  def __int__(self):

    if   type(self.data) == float: return int(self.data)
    elif type(self.data) == int  : return self.data
    else                         : return 0

  # ----------------------- return numeric value as float, or return a dummy -----------------------

  def __float__(self):

    if   type(self.data) == float: return self.data
    elif type(self.data) == int  : return float(self.data)
    else                         : return 0.0

  # -------------- compare two numeric values, use fixed rules if one is not numeric ---------------

  def __lt__(self,other):

    if   self .isnumeric() and other.isnumeric(): return float(self) < float(other)
    elif self .isnumeric()                      : return  0
    elif other.isnumeric()                      : return -1
    else                                        : return self.data < other.data

# ============================ CLASS TO REPRESENT A DURATION IN SECONDS ============================

class Time(Integer):

  # ------------------------------------------- __init__ -------------------------------------------

  def __init__(self,*args,**kwargs):

    self.precision = kwargs.pop('precision',None)

    super().__init__(*args,**kwargs)

  # ------------- convert number + unit -> string, formatted to the correct precision --------------

  def asunit(self,n,unit):

    if self.precision:
      return '{{0:.{precision:d}f}}{{1:s}}'.format(**self.__dict__).format(n,unit)
    else:
      if abs(round(n)) < 10.: return '{0:.1f}{1:s}'.format(      n ,unit)
      else                  : return '{0:.0f}{1:s}'.format(round(n),unit)

  # ---------------- return string, formatted to fixed precision with relevant unit ----------------

  def __str__(self):

    if not self.isnumeric(): return self.data

    base = [60*60*24, 60*60, 60, 1]
    name = ['d', 'h', 'm', 's']

    for i,unit in zip(base,name):
      if abs(self.data) >= i:
        return self.asunit(float(self.data)/float(i), unit)

    return self.asunit(float(self.data), 's')

# =============================== CLASS TO REPRESENT MEMORY IN BYTES ===============================

class Memory(Integer):

  # ------------------------------------------- __init__ -------------------------------------------

  def __init__(self,*args,**kwargs):

    self.precision = kwargs.pop('precision',None)

    super().__init__(*args,**kwargs)

  # ------------- convert number + unit -> string, formatted to the correct precision --------------

  def asunit(self,n,unit):

    if self.precision:
      return '{{0:.{precision:d}f}}{{1:s}}'.format(**self.__dict__).format(n,unit)
    else:
      return '{0:.0f}{1:s}'.format(round(n),unit)

  # ---------------- return string, formatted to fixed precision with relevant unit ----------------

  def __str__(self):

    if not self.isnumeric(): return self.data

    base = [1e12, 1e9, 1e6, 1e3, 1]
    name = ['T', 'G', 'M', 'K', 'B']

    for i,unit in zip(base,name):
      if abs(self.data) >= i:
        return self.asunit(float(self.data)/float(i), unit)

    return self.asunit(float(self.data), 'B')
