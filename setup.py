
from setuptools                 import setup
from setuptools.command.install import install

# --------------------------------------------------------------------------------------------------

__version__ = '0.0.1'

# --------------------------------------------------------------------------------------------------

setup(
  name              = 'GooseSLURM',
  version           = __version__,
  author            = 'Tom de Geus',
  author_email      = 'tom@geus.me',
  url               = 'https://github.com/tdegeus/GooseSLURM',
  keywords          = 'SLURM',
  description       = 'Support functions for SLURM',
  long_description  = '',
  license           = 'MIT',
  packages          = ['GooseSLURM'],
)

# --------------------------------------------------------------------------------------------------
