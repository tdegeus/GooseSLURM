from pathlib import Path

from setuptools import find_packages
from setuptools import setup

project_name = "GooseSLURM"

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=project_name,
    license="MIT",
    author="Tom de Geus",
    author_email="tom@geus.me",
    description="Support functions for SLURM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="SLURM",
    url=f"https://github.com/tdegeus/{project_name:s}",
    packages=find_packages(exclude=["tests"]),
    use_scm_version={"write_to": f"{project_name}/_version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["click", "tqdm", "PyYAML", "numpy"],
    entry_points={
        "console_scripts": [
            f"Gdel = {project_name}.cli.Gdel:main",
            f"Ginfo = {project_name}.cli.Ginfo:main",
            f"Gps = {project_name}.cli.Gps:main",
            f"Gstat = {project_name}.cli.Gstat:main",
            f"Gsub = {project_name}.cli.Gsub:main",
            f"Gacct = {project_name}.sacct:_Gacct_catch",
        ]
    },
)
