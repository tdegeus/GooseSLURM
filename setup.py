
from setuptools import setup
from setuptools import find_packages

setup(
    name = 'GooseSLURM',
    version = '0.1.0',
    license = 'MIT',
    author = 'Tom de Geus',
    author_email = 'tom@geus.me',
    description = 'Support functions for SLURM',
    long_description = 'Support functions for SLURM',
    keywords = 'SLURM',
    url = 'https://github.com/tdegeus/GooseSLURM',
    packages = find_packages(),
    install_requires = ['docopt>=0.6.2', 'click>=4.0'],
    entry_points = {
          'console_scripts': [
               'Gdel = GooseHDF5.cli.Gdel:main',
               'Ginfo = GooseHDF5.cli.Ginfo:main',
               'Gps = GooseHDF5.cli.Gps:main',
               'Gstat = GooseHDF5.cli.Gstat:main',
               'Gsub = GooseHDF5.cli.Gsub:main']})
