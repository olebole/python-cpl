Log messages
============

We provide CPL log messages in three different ways: as CPL defined terminal
messages, via Python logging, and as a list of messages in the
:class:`cpl.Result` object

.. currentmodule:: cpl.log

Python style logging
--------------------

The preferred and most flexible way to do logging is the use of the
:module:`logging` module of Python. A basic setup (similar to the style used
in esorex) is::

  log = logging.getLogger()
  log.setLevel(logging.INFO)
  ch = logging.FileHandler('muse_pipeline.log')
  ch.setLevel(logging.INFO)
  fr = logging.Formatter('%(created)s [%(levelname)s] %(name)s: %(message)s',
                         '%H:%M:%S')
  ch.setFormatter(fr)
  log.addHandler(ch)

The default basic log name for CPL log messages in the recipes is
`cpl.<recipename>`. The log name can be changed with the `logname` parameter
of the recipe call to follow own naming rules, or to separate the output of
parallel outputs::

  res = [ muse_focus(f, logname = 'cpl.muse_focus%02i' % (i+1)) 
          for i, f in enumerate(inputfiles) ]

To the basic log name the function name is appended to allow selective logging
of a certain function. The following sample code::

  dlog = logging.getLogger('cpl.muse_sky.muse_sky_create_skymask')
  dlog.setLevel(logging.DEBUG)
  ch = logging.FileHandler('sky_create_skymask.log')
  ch.setLevel(logging.DEBUG)
  fr = logging.Formatter('%(relativeCreated)d [%(levelname)s] %(message)s')
  ch.setFormatter(fr)
  dlog.addHandler(ch)

will create a log file that contains only the debug messages for the function
call muse_sky_create_skymask(). 

.. note:: Since the log messages are cached in CPL, they may occur with some
   delay in the python log module. Also, log messages from different recipes
   running in parallel may be mixed in their chronological order. The
   resolution of the log time stamp is one second.

Log message lists
-----------------

The :class:`cpl.Result` object as well as a :class:`cpl.CplException` have an
attribute :attrib:`cpl.Result.log` that contains the list of all log messages.

.. autoclass:: cpl.log.LogList

.. autoattribute:: cpl.log.LogList.error

.. autoattribute:: cpl.log.LogList.warn

.. autoattribute:: cpl.log.LogList.info

.. autoattribute:: cpl.log.LogList.debug


Terminal messages
-----------------

.. data:: cpl.msg

This variable is a :class:`CplLogger` instance and provides an interface to the
terminal logging functionality of the CPL. The following messages allow to
setup terminal messages similar to the according CPL functions:

    .. autoattribute:: cpl.log.CplLogger.level 

    .. autoattribute:: cpl.log.CplLogger.time

    .. autoattribute:: cpl.log.CplLogger.domain

.. deprecated:: 0.3
   Use :class:`logging.StreamLogger` instead.

Calling CPL messages from Python
--------------------------------

.. automethod:: cpl.log.Logger.debug

.. automethod:: cpl.log.Logger.info

.. automethod:: cpl.log.Logger.warn

.. automethod:: cpl.log.Logger.error

.. automethod:: cpl.log.Logger.indent_more

.. automethod:: cpl.log.Logger.indent_less

.. deprecated:: 0.3
   Use :module:`logging` instead.

