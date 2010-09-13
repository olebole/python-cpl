.. Python bindings for CPL recipes documentation master file, created by
   sphinx-quickstart on Sat Aug 28 10:52:22 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. title:: The CPL recipe python interface

:mod:`cpl` The CPL recipe python interface
##########################################

.. module:: cpl

This is a non-official python module to access CPL recipes. It is not meant as
part of the CPL or the MUSE pipeline software, but may be useful for testing
and analysis.

The Common Pipeline Library (CPL) consists of a set of C libraries, which have
been developed to standardise the way VLT instrument pipelines are built, to
shorten their development cycle and to ease their maintenance.  The Common
Pipeline Library was not designed as a general purpose image processing
library, but rather to address two primary requirements. The first of these
was to provide an interface to the VLT pipeline runtime- environment. The
second was to provide a software kit of medium-level tools, which allows
astronomical data-reduction tasks to be built rapidly.

.. toctree::
   :numbered:

   install
   tutorial
   recipe
   parallel
   param
   frames
   result
   msg
   esorex
   restrictions

You can also `download a PDF version
<http://github.com/downloads/olebole/python-cpl/python-cpl.pdf>` of the user
manual.

Feedback
========

Send python specific questions to ole@aip.de. Questions regading CPL should
mailed to cpl-help@eso.org.

