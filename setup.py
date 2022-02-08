from setuptools import find_packages
from setuptools import setup

setup(
    name="GooseSLURM",
    license="MIT",
    author="Tom de Geus",
    author_email="tom@geus.me",
    description="Support functions for SLURM",
    long_description="Support functions for SLURM",
    keywords="SLURM",
    url="https://github.com/tdegeus/GooseSLURM",
    packages=find_packages(),
    use_scm_version={"write_to": "GooseSLURM/_version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["click", "tqdm", "PyYAML"],
    entry_points={
        "console_scripts": [
            "Gdel = GooseSLURM.cli.Gdel:main",
            "Ginfo = GooseSLURM.cli.Ginfo:main",
            "Gps = GooseSLURM.cli.Gps:main",
            "Gstat = GooseSLURM.cli.Gstat:main",
            "Gsub = GooseSLURM.cli.Gsub:main",
        ]
    },
)
