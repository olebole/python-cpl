Log messages
============

We provide CPL log messages in two different ways: via Python logging and as
a list of messages in the :class:`cpl.Result` object.

For convienience, simple terminal messages and predefined log file output in a
style similar to the original CPL messages.

.. currentmodule:: cpl.logger

Python style logging
--------------------

The preferred and most flexible way to do logging is the use of the
:mod:`logging` module of Python. A basic setup (similar to the style used
in `esorex <http://www.eso.org/sci/software/cpl/esorex.html>`_) is::

  import logging

  log = logging.getLogger()
  log.setLevel(logging.INFO)
  ch = logging.FileHandler('cpl_recipe.log')
  ch.setLevel(logging.INFO)
  fr = logging.Formatter('%(created)s [%(levelname)s] %(name)s: %(message)s',
                         '%H:%M:%S')
  ch.setFormatter(fr)
  log.addHandler(ch)

The default basic log name for CPL log messages in the recipes is
:file:`cpl.{recipename}`. The log name can be changed with the ``logname``
parameter of :class:`cpl.Recipe.__call__()` to follow own naming rules, or to
separate the output of recipes that are executed in parallel::

  res = [ muse_focus(f, logname = 'cpl.muse_focus%02i' % (i+1), threading = True) 
          for i, f in enumerate(inputfiles) ]

To the basic log name the function name is appended to allow selective logging
of a certain function. The following sample line::

  logging.getLogger('cpl.muse_sky.muse_sky_create_skymask').setLevel(logging.DEBUG)

will log the debug messages from :func:`muse_sky_create_skymask()`
additionally to the other messages.

.. note::

   Since the log messages are cached in CPL, they may occur with some
   delay in the python log module. Also, log messages from different recipes
   running in parallel may be mixed in their chronological order. The
   resolution of the log time stamp is one second. The fields
   :attr:`logging.LogRecord.args`, :attr:`logging.LogRecord.exc_info` and
   :attr:`logging.LogRecord.lineno` are not set. Also, due to limitations in
   the CPL logging module, level filtering is done only after the creation of
   the log entries. This may cause performance problems if extensive debug
   logging is done and filtered out by :class:`logging.Logger.setLevel()`. In
   this case the :class:`cpl.Recipe.__call__()` parameter ``loglevel`` may be
   used.

.. seealso :: :data:`cpl.esorex.msg` and :data:`cpl.esorex.log`

   EsoRex like convienience logging.

Log message lists
-----------------

The :class:`cpl.Result` object as well as a :class:`cpl.CplError` have an
attribute :attr:`cpl.Result.log` resp. :attr:`cpl.CplError.log` that contains
the :class:`list` of all log messages.

.. autoclass:: cpl.logger.LogList

   .. autoattribute:: cpl.logger.LogList.error

   .. autoattribute:: cpl.logger.LogList.warning

   .. autoattribute:: cpl.logger.LogList.info

   .. autoattribute:: cpl.logger.LogList.debug


