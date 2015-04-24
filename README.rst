python-cpl
==========

*Python interface for the Common Pipeline Library*

.. image:: https://pypip.in/v/python-cpl/badge.png
    :target: https://pypi.python.org/pypi/python-cpl

.. image:: https://pypip.in/d/python-cpl/badge.png
    :target: https://pypi.python.org/pypi/python-cpl

This module can list, configure and execute CPL-based recipes from Python
(python2 and python3).  The input, calibration and output data can be
specified as FITS files or as ``astropy.io.fits`` objects in memory.

The ESO `Common Pipeline Library <http://www.eso.org/sci/software/cpl/>`_
(CPL) comprises a set of ISO-C libraries that provide a comprehensive,
efficient and robust software toolkit. It forms a basis for the creation of
automated astronomical data-reduction tasks. One of the features provided by
the CPL is the ability to create data-reduction algorithms that run as plugins
(dynamic libraries). These are called "recipes" and are one of the main
aspects of the CPL data-reduction development environment.

Python-cpl releases are `registered on PyPI
<http://pypi.python.org/pypi/python-cpl>`_, and development is occurring at
the `project's github page <http://github.com/olebole/python-cpl>`_.

For installation instructions, see the 
`online documentation <http://cpl-python.readthedocs.org/en/master/install.html>`_
or ``docs/install.rst`` in this source distribution.
The travis test status, coverage, and documentation build status
of the github repository is:

.. image:: https://travis-ci.org/olebole/python-cpl.png
    :target: https://travis-ci.org/olebole/python-cpl

.. image:: https://coveralls.io/repos/olebole/python-cpl/badge.svg?branch=master
  :target: https://coveralls.io/r/olebole/python-cpl?branch=master

.. image:: https://readthedocs.org/projects/python-cpl/badge/?version=latest
    :target: https://readthedocs.org/projects/python-cpl/?badge=latest

