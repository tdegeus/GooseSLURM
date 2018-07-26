
from . import duration
from . import memory

# ==================================================================================================

class String:
  r'''
Rich string.

.. note::

  All options are attributes, that can be modified at all times.

:options:

  **data** (``<str>`` | ``None``)
    The data.

  **width** ([``None``] | ``<int>``)
    Print width (formatted print only).

  **color** ([``None``] | ``<str>``)
    Print color, e.g. "1;32" for bold green (formatted print only).

  **align** ([``'<'``] | ``'>'``)
    Print alignment (formatted print only).

  **dummy** ([``0``] | ``<int>`` | ``<float>``)
    Dummy numerical value.

:methods:

  **A.format()**
    Formatted string.

  **str(A)**
    Unformatted string.

  **A.isnumeric()**
    Return if the "data" is numeric.

  **int(A)**
    Dummy integer.

  **float(A)**
    Dummy float.
  '''

  # ------------------------------------------------------------------------------------------------

  def __init__(self, data, width=None, align='<', color=None, dummy=0):

    self.data  = data
    self.width = width
    self.color = color
    self.align = align
    self.dummy = dummy

  # ------------------------------------------------------------------------------------------------

  def format(self):
    r'''
Return formatted string: align/width/color are applied.
    '''

    if self.width and self.color:
      fmt = '\x1b[{color:s}m{{0:{align:s}{width:d}.{width:d}s}}\x1b[0m'.format(**self.__dict__)
    elif self.width:
      fmt = '{{0:{align:s}{width:d}.{width:d}s}}'.format(**self.__dict__)
    elif self.color:
      fmt = '\x1b[{color:s}m{{0:{align:s}s}}\x1b[0m'.format(**self.__dict__)
    else:
      fmt = '{{0:{align:s}s}}'.format(**self.__dict__)

    return fmt.format(str(self))

  # ------------------------------------------------------------------------------------------------

  def isnumeric(self):
    r'''
Return if the "data" is numeric : always zero for this class.
    '''

    return False

  # ------------------------------------------------------------------------------------------------

  def __str__(self):

    return str(self.data)

  # ------------------------------------------------------------------------------------------------

  def __int__(self):

    return int(self.dummy)

  # ------------------------------------------------------------------------------------------------

  def __float__(self):

    return float(self.dummy)

  # ------------------------------------------------------------------------------------------------

  def __repr__(self):

    return str(self)

  # ------------------------------------------------------------------------------------------------

  def __lt__(self,other):

    return str(self) < str(other)

# ==================================================================================================

class Integer(String):
  r'''
Rich integer.

.. note::

  All options are attributes, that can be modified at all times.

:options:

  **data** (``<str>`` | ``None``)
    The data.

  **width** ([``None``] | ``<int>``)
    Print width (formatted print only).

  **color** ([``None``] | ``<str>``)
    Print color, e.g. "1;32" for bold green (formatted print only).

  **align** ([``'<'``] | ``'>'``)
    Print alignment (formatted print only).

  **dummy** ([``0``] | ``<int>`` | ``<float>``)
    Dummy numerical value, used in case of non-numerical ``data``.

:methods:

  **A.format()**
    Formatted string.

  **str(A)**
    Unformatted string.

  **A.isnumeric()**
    Return if the "data" is numeric.

  **int(A)**
    Return ``data`` as integer (``dummy`` is returned if ``data`` is not numeric).

  **float(A)**
    Return ``data`` as float (``dummy`` is returned if ``data`` is not numeric).
  '''

  # ------------------------------------------------------------------------------------------------

  def __init__(self,data,**kwargs):

    try   : data = int(data)
    except: pass

    super().__init__(data,**kwargs)

  # ------------------------------------------------------------------------------------------------

  def isnumeric(self):
    r'''
Return if the "data" is numeric : always zero for this class.
    '''

    if type(self.data) == int  : return True
    if type(self.data) == float: return True

    return False

  # ------------------------------------------------------------------------------------------------

  def __int__(self):

    if type(self.data) == int  : return self.data
    if type(self.data) == float: return int(self.data)

    return int(self.dummy)

  # ------------------------------------------------------------------------------------------------

  def __float__(self):

    if type(self.data) == int  : return float(self.data)
    if type(self.data) == float: return self.data

    return float(self.dummy)

  # ------------------------------------------------------------------------------------------------

  def __lt__(self,other):

    if   self .isnumeric() and other.isnumeric(): return int(self) < int(other)
    elif self .isnumeric()                      : return  0
    elif other.isnumeric()                      : return -1

    return self.data < other.data

# ==================================================================================================

class Float(String):
  r'''
Rich float.

.. note::

  All options are attributes, that can be modified at all times.

:options:

  **data** (``<str>`` | ``None``)
    The data.

  **width** ([``None``] | ``<int>``)
    Print width (formatted print only).

  **color** ([``None``] | ``<str>``)
    Print color, e.g. "1;32" for bold green (formatted print only).

  **align** ([``'<'``] | ``'>'``)
    Print alignment (formatted print only).

  **precision** ([``2``] | ``<int>``)
    Print precision (formatted print only).

  **dummy** ([``0``] | ``<int>`` | ``<float>``)
    Dummy numerical value, used in case of non-numerical ``data``.

:methods:

  **A.format()**
    Formatted string.

  **str(A)**
    Unformatted string.

  **A.isnumeric()**
    Return if the "data" is numeric.

  **int(A)**
    Return ``data`` as integer (``dummy`` is returned if ``data`` is not numeric).

  **float(A)**
    Return ``data`` as float (``dummy`` is returned if ``data`` is not numeric).
  '''

  # ------------------------------------------------------------------------------------------------

  def __init__(self,data,**kwargs):

    try   : data = float(data)
    except: pass

    self.precision = kwargs.pop('precision',2)

    super().__init__(data,**kwargs)

  # ------------------------------------------------------------------------------------------------

  def isnumeric(self):
    r'''
Return if the "data" is numeric : always zero for this class.
    '''

    if type(self.data) == float: return True
    if type(self.data) == int  : return True

    return False

  # ------------------------------------------------------------------------------------------------

  def __str__(self):

    if not self.isnumeric(): return self.data

    return '{{0:.{precision:d}f}}'.format(**self.__dict__).format(self.data)

  # ------------------------------------------------------------------------------------------------

  def __int__(self):

    if type(self.data) == float: return int(self.data)
    if type(self.data) == int  : return self.data

    return int(self.dummy)

  # ------------------------------------------------------------------------------------------------

  def __float__(self):

    if type(self.data) == float: return self.data
    if type(self.data) == int  : return float(self.data)

    return float(self.dummy)

  # ------------------------------------------------------------------------------------------------

  def __lt__(self,other):

    if   self .isnumeric() and other.isnumeric(): return float(self) < float(other)
    elif self .isnumeric()                      : return  0
    elif other.isnumeric()                      : return -1

    return self.data < other.data

# ==================================================================================================

class Duration(Integer):
  r'''
Rich duration (seconds: integer).

.. note::

  All options are attributes, that can be modified at all times.

:options:

  **data** (``<str>`` | ``None``)
    The data.

  **width** ([``None``] | ``<int>``)
    Print width (formatted print only).

  **color** ([``None``] | ``<str>``)
    Print color, e.g. "1;32" for bold green (formatted print only).

  **align** ([``'<'``] | ``'>'``)
    Print alignment (formatted print only).

  **precision** ([``None``] | ``<int>``)
    Print precision to use for the conversion (formatted print only). ``None`` means automatic
    precision. See ``GooseSLURM.duration.asHuman``.

  **dummy** ([``0``] | ``<int>`` | ``<float>``)
    Dummy numerical value, used in case of non-numerical ``data``.

:methods:

  **A.format()**
    Formatted string, after unit conversion.

  **str(A)**
    Unformatted string, after unit conversion.

  **A.isnumeric()**
    Return if the "data" is numeric.

  **int(A)**
    Return ``data`` as integer (``dummy`` is returned if ``data`` is not numeric).

  **float(A)**
    Return ``data`` as float (``dummy`` is returned if ``data`` is not numeric).
  '''

  # ------------------------------------------------------------------------------------------------

  def __init__(self,data,**kwargs):

    data = duration.asSeconds(data, default=data)

    self.precision = kwargs.pop('precision', None)

    super().__init__(data,**kwargs)

  # ------------------------------------------------------------------------------------------------

  def __str__(self):

    if not self.isnumeric(): return self.data

    return duration.asHuman(self.data, self.precision)

# ==================================================================================================

class Memory(Integer):
  r'''
Rich memory (seconds: integer).

.. note::

  All options are attributes, that can be modified at all times.

:options:

  **data** (``<str>`` | ``None``)
    The data.

  **width** ([``None``] | ``<int>``)
    Print width (formatted print only).

  **color** ([``None``] | ``<str>``)
    Print color, e.g. "1;32" for bold green (formatted print only).

  **align** ([``'<'``] | ``'>'``)
    Print alignment (formatted print only).

  **precision** ([``None``] | ``<int>``)
    Print precision to use for the conversion (formatted print only). ``None`` means automatic
    precision. See ``GooseSLURM.memory.asHuman``.

  **dummy** ([``0``] | ``<int>`` | ``<float>``)
    Dummy numerical value, used in case of non-numerical ``data``.

:methods:

  **A.format()**
    Formatted string, after unit conversion.

  **str(A)**
    Unformatted string, after unit conversion.

  **A.isnumeric()**
    Return if the "data" is numeric.

  **int(A)**
    Return ``data`` as integer (``dummy`` is returned if ``data`` is not numeric).

  **float(A)**
    Return ``data`` as float (``dummy`` is returned if ``data`` is not numeric).
  '''

  # ------------------------------------------------------------------------------------------------

  def __init__(self,data,**kwargs):

    data = memory.asBytes(data, default=data)

    self.precision = kwargs.pop('precision', None)

    super().__init__(data,**kwargs)

  # ------------------------------------------------------------------------------------------------

  def __str__(self):

    if not self.isnumeric(): return self.data

    return memory.asHuman(self.data, self.precision)
