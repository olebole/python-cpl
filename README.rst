python-cpl
==========

*Python interface for the Common Pipeline Library*

.. image:: https://img.shields.io/pypi/v/python-cpl.svg
    :target: https://pypi.python.org/pypi/python-cpl

Python-cpl is an `Astropy Affiliated Package <http://www.astropy.org/affiliated/>`_
that can list, configure and execute recipes from `ESO data reduction
pipelines <http://www.eso.org/sci/software/pipelines/>`_ from Python
(python2 and python3).  The input, calibration and output data can be
specified as FITS files or as ``astropy.io.fits`` objects in memory.

The ESO `Common Pipeline Library <http://www.eso.org/sci/software/cpl/>`_
(CPL) comprises a set of ISO-C libraries that provide a comprehensive,
efficient and robust software toolkit. It forms a basis for the creation of
automated astronomical data-reduction tasks. One of the features provided by
the CPL is the ability to create data-reduction algorithms that run as plugins
(dynamic libraries). These are called "recipes" and are one of the main
aspects of the CPL data-reduction development environment.

Python-CPL releases are `registered on PyPI
<http://pypi.python.org/pypi/python-cpl>`_, and development is occurring at
the `project's github page <http://github.com/olebole/python-cpl>`_.

For installation instructions, see the
`online documentation <http://python-cpl.readthedocs.org/en/latest/install.html>`_.
The travis test status, coverage, and documentation build status
of the github repository is:

.. image:: https://travis-ci.org/olebole/python-cpl.png
    :target: https://travis-ci.org/olebole/python-cpl

.. image:: https://coveralls.io/repos/olebole/python-cpl/badge.svg?branch=master
  :target: https://coveralls.io/r/olebole/python-cpl?branch=master

.. image:: https://landscape.io/github/olebole/python-cpl/master/landscape.svg?style=flat
   :target: https://landscape.io/github/olebole/python-cpl/master

.. image:: https://readthedocs.org/projects/python-cpl/badge/?version=latest
    :target: https://readthedocs.org/projects/python-cpl/?badge=latest

