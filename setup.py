
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
               'Gdel = GooseSLURM.cli.Gdel:main',
               'Ginfo = GooseSLURM.cli.Ginfo:main',
               'Gps = GooseSLURM.cli.Gps:main',
               'Gstat = GooseSLURM.cli.Gstat:main',
               'Gsub = GooseSLURM.cli.Gsub:main']})
