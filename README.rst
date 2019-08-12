PIE-scope: integrated cryo-correlative light and FIB/SEM microscopy

|appveyor-build-status| |travis-build-status| |docs|

Installation
============

Install or upgrade to the latest version directly from GitHub with:

.. code-block::

   pip install git+https://github.com/DeMarcoLab/piescope.git

You can check what version you're currently using in python:

.. code-block:: python

   import piescope
   piescope.__version__

Runing the program
==================

See all the command line options available with:

.. code-block::

   python -m piescope --help


.. |appveyor-build-status| image:: https://ci.appveyor.com/api/projects/status/m3s3g96phg9m3p06/branch/develop?svg=true
    :alt: Appveyor build status
    :target: https://ci.appveyor.com/project/GenevieveBuckley/piescope

.. |travis-build-status| image:: https://travis-ci.com/DeMarcoLab/piescope.svg?branch=develop
    :alt: Travis build status
    :target: https://travis-ci.com/DeMarcoLab/piescope

.. |docs| image:: https://readthedocs.org/projects/piescope/badge/?version=develop
    :alt: Documentation Status
    :target: https://piescope.readthedocs.io/en/develop/?badge=develop
