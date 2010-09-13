:data:`cpl.msg`: Log messages
=============================
.. data:: cpl.msg

This variable is a :class:`Logger` instance and provides an interface to the
logging functionality of the CPL.

Basic setup
-----------
.. currentmodule:: cpl.log

.. autoattribute:: Logger.level 

.. autoattribute:: cpl.log.Logger.time

.. automethod:: cpl.log.Logger.logfile

.. autoattribute:: cpl.log.Logger.file

.. autoattribute:: cpl.log.Logger.domain

Logging from the python script
------------------------------

.. automethod:: cpl.log.Logger.debug

.. automethod:: cpl.log.Logger.info

.. automethod:: cpl.log.Logger.warn

.. automethod:: cpl.log.Logger.error

.. automethod:: cpl.log.Logger.indent_more

.. automethod:: cpl.log.Logger.indent_less
