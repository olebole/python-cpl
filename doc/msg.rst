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

.. autoattribute:: cpl.log.Logger.domain

.. autoclass:: cpl.log.LogList

.. autoattribute:: cpl.log.LogList.error

.. autoattribute:: cpl.log.LogList.warn

.. autoattribute:: cpl.log.LogList.info

.. autoattribute:: cpl.log.LogList.debug

Logging from the python script
------------------------------

.. automethod:: cpl.log.Logger.debug

.. automethod:: cpl.log.Logger.info

.. automethod:: cpl.log.Logger.warn

.. automethod:: cpl.log.Logger.error

.. automethod:: cpl.log.Logger.indent_more

.. automethod:: cpl.log.Logger.indent_less
