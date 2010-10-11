:class:`cpl.Recipe` The Recipe interface
========================================

.. module:: cpl

.. class:: cpl.Recipe

   Recipes are loaded from shared libraries that are provided with the
   pipeline library of the instrument.

.. attribute:: Recipe.path

   Search path for the recipes. It may be set to either a string, or to a list
   of strings. All shared libraries in the search path and their
   subdirectories are searched for CPL recipes. On default, the path is set to
   the current directory.

   The search path is automatically set to the esorex path when
   :func:`cpl.esorex.init()` is called.

.. automethod:: Recipe.list

.. automethod:: Recipe.set_maxthreads

   .. seealso:: :ref:`parallel`

Constructor
-----------

.. automethod:: Recipe.__init__

Common attributes and methods
-----------------------------

These attributes and methods are available for all recipes.

.. attribute:: Recipe.name 

   Recipe name

.. autoattribute:: Recipe.version

.. attribute:: Recipe.filename

   Shared library file name.

.. autoattribute:: Recipe.author

.. autoattribute:: Recipe.description

.. attribute:: Recipe.output_dir

   Output directory if specified, or :keyword:`None`.

.. attribute:: Recipe.temp_dir

   Base directory for temporary directories where the recipe is
   executed. The working dir is created as a subdir with a random file
   name. Defaults to :literal:`'.'`.

.. attribute:: Recipe.threaded

   Specify whether the recipe should be executed synchroniously or as an
   extra process in the background.

   .. seealso:: :ref:`parallel`

.. attribute:: Recipe.tag

   Default tag when the recipe is called. This is set automatically only
   if the recipe provided the information about input tags. Otherwise
   this tag has to be set manually.

.. autoattribute:: Recipe.tags

.. automethod:: Recipe.output

Recipe parameters
-----------------

Recipe parameters may be set either via the :attr:`Recipe.param` attribute or
as named keywords on the run execution. A value set in the recipe call will
overwrite any value that was set previously in the :attr:`Recipe.param`
attribute for that specific call.

.. autoattribute:: Recipe.param
.. seealso:: :class:`cpl.Parameter`

Recipe frames
-------------

There are three groups of frames: calibration ("calib") frames, input ("raw")
frames, and result ("product") frames.  Calibration frames may be set either
via the :attr:`Recipe.calib` attribute or as named keywords on the run
execution. A value set in the recipe call will overwrite any value that was
set previously in the :attr:`Recipe.calib` attribute for that specific
call. Input frames are always set in the recipe call. If their tag name was
not given, the tag name from :attr:`Recipe.tag` is used if the recipe provides
it.

.. autoattribute:: Recipe.calib
.. seealso:: :class:`cpl.FrameConfig`

Recipe invocation
-----------------

.. automethod:: Recipe.__call__

.. seealso:: :ref:`parallel`
