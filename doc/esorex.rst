.. module:: cpl

:mod:`cpl.esorex` :program:`EsoRex` legacy support
==================================================

.. automodule:: cpl.esorex

Support for configuration and SOF files
---------------------------------------

.. autofunction:: init
.. autofunction:: load_rc
.. autofunction:: load_sof

Convienence logging control
---------------------------

.. autodata:: msg

   The following attributes control the format of the terminal messages:

   .. autoattribute:: cpl.esorex.CplLogger.level
   .. autoattribute:: cpl.esorex.CplLogger.format
   .. autoattribute:: cpl.esorex.CplLogger.time
   .. autoattribute:: cpl.esorex.CplLogger.component
   .. autoattribute:: cpl.esorex.CplLogger.threadid

.. autodata:: log

   The following attributes control the format of the log file messages:

   .. autoattribute:: cpl.esorex.CplLogger.filename
   .. attribute:: CplLogger.dir

      Directory name that is prepended to the log file name.

   .. autoattribute:: cpl.esorex.CplLogger.level
   .. autoattribute:: cpl.esorex.CplLogger.format
   .. autoattribute:: cpl.esorex.CplLogger.time
   .. autoattribute:: cpl.esorex.CplLogger.component
   .. autoattribute:: cpl.esorex.CplLogger.threadid
