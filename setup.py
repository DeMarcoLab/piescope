import os
from setuptools import setup, find_packages

from piescope._version import __version__


def parse_requirements_file(filename):
    with open(filename) as fid:
        requires = [l.strip() for l in fid.readlines() if l]

    return requires


descr = """DeMarco lab PIE-scope package."""

DISTNAME = 'piescope'
DESCRIPTION = 'Integrated correlative light-electron microscopy tool'
LONG_DESCRIPTION = descr
AUTHOR_EMAIL = 'Patrick.Cleeve@monash.edu, David.Dierickx1@monash.edu'
MAINTAINERS = 'Patrick Cleeve, David Dierickx'
URL = 'https://github.com/DeMarcoLab/piescope'
DOWNLOAD_URL = 'https://github.com/DeMarcoLab/piescope'
VERSION = __version__
PYTHON_VERSION = (3, 7)
INST_DEPENDENCIES = parse_requirements_file(
    'requirements.txt'
)

if __name__ == '__main__':
    setup(
        name=DISTNAME,
        version=__version__,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=MAINTAINERS,
        author_email=AUTHOR_EMAIL,
        packages=find_packages(),
        install_requires=INST_DEPENDENCIES,
    )
