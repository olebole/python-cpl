.. module:: cpl

:mod:`cpl.esorex` Esorex legacy support
=======================================

.. automodule:: cpl.esorex

.. autofunction:: init
.. autofunction:: load_rc
.. autofunction:: load_sof

Convienence logging control
---------------------------

.. data:: msg

   This variable is a :class:`CplLogger` instance that provides a convienience
   stream handler similar to the terminal logging functionality of the CPL. It
   basically does the same as::

     import logging

     log = logging.getLogger()
     log.setLevel(logging.INFO)
     ch = logging.StreamHandler()
     ch.setLevel(logging.INFO)
     ch.setFormatter(logging.Formatter('[%(levelname)7s] %(message)s'))
     log.addHandler(ch)

   The following attributes control the format of the terminal messages:

   .. currentclass: cpl.esorex.CplLogger

   .. autoattribute:: cpl.esorex.CplLogger.level

   .. autoattribute:: cpl.esorex.CplLogger.format

   .. autoattribute:: cpl.esorex.CplLogger.time

   .. autoattribute:: cpl.esorex.CplLogger.component

   .. autoattribute:: cpl.esorex.CplLogger.threadid

.. data:: log

   This variable is a :class:`CplLogger` instance that provides a convienience
   file handler similar to the file logging functionality of the CPL. It
   basically does the same as::

    import logging

    log = logging.getLogger()
    log.setLevel(logging.INFO)
    ch = logging.FileHandler(filename)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)7s] %(funcName)s: %(message)s'))
    log.addHandler(ch)

   The following attributes control the format of the log file messages:

   .. currentclass: cpl.esorex.CplLogger

   .. autoattribute:: cpl.esorex.CplLogger.filename

   .. attribute:: CplLogger.dir

      Directory name that is prepended to the log file name.

   .. autoattribute:: cpl.esorex.CplLogger.level

   .. autoattribute:: cpl.esorex.CplLogger.format

   .. autoattribute:: cpl.esorex.CplLogger.time

   .. autoattribute:: cpl.esorex.CplLogger.component

   .. autoattribute:: cpl.esorex.CplLogger.threadid
