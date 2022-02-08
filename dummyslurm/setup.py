from setuptools import find_packages
from setuptools import setup

setup(
    name="dummyslurm",
    license="MIT",
    author="Tom de Geus",
    author_email="tom@geus.me",
    description="Dummy slurm installation",
    long_description="Dummy slurm installation",
    keywords="SLURM",
    url="https://github.com/tdegeus/GooseSLURM",
    packages=find_packages(),
    install_requires=["PyYAML"],
    entry_points={
        "console_scripts": [
            "sacct = dummyslurm:sacct",
            "sbatch = dummyslurm:sbatch",
            "scancel = dummyslurm:scancel",
            "scontrol = dummyslurm:scontrol",
            "squeue = dummyslurm:squeue",
        ]
    },
)
