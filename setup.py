from setuptools import setup, find_packages

from piescope._version import __version__

descr = """DeMarco lab FIB-SEM package for automated controls."""

DISTNAME = 'piescope'
DESCRIPTION = 'DeMarco lab FIB-SEM tools.'
LONG_DESCRIPTION = descr
MAINTAINER = 'Genevieve Buckley'
URL = 'https://github.com/DeMarcoLab/piescope'
DOWNLOAD_URL = 'https://github.com/DeMarcoLab/piescope'
VERSION = __version__
PYTHON_VERSION = (3, 5)
INST_DEPENDENCIES = []

if __name__ == '__main__':
    setup(name=DISTNAME,
          version=__version__,
          url=URL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          author=MAINTAINER,
          packages=find_packages(),
          install_requires=INST_DEPENDENCIES
          )
