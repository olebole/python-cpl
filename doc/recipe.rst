.. module:: cpl

The Recipe interface
====================

.. autoclass:: Recipe

Static members
--------------

.. autoattribute:: Recipe.path
.. autoattribute:: Recipe.memory_mode
.. automethod:: Recipe.list()
.. automethod:: Recipe.set_maxthreads(n)

Constructor
-----------

.. automethod:: Recipe.__init__

Common attributes and methods
-----------------------------

These attributes and methods are available for all recipes.

.. attribute:: Recipe.__name__

   Recipe name.

.. autoinstanceattribute:: Recipe.__file__

   Shared library file name.

.. autoattribute:: Recipe.__author__
.. autoattribute:: Recipe.__email__
.. autoattribute:: Recipe.__copyright__
.. autoattribute:: Recipe.description
.. autoattribute:: Recipe.version
.. autoattribute:: Recipe.cpl_version
.. autoattribute:: Recipe.cpl_description
.. attribute:: Recipe.output_dir

   Output directory if specified, or :obj:`None`. The recipe will write the
   output files into this directory and return their file names. If the
   directory does not exist, it will be created before the recipe is
   executed. Output files within the output directory will be silently
   overwritten. If no output directory is set, the recipe call will result in
   :class:`astropy.io.fits.HDUList` result objects. The output directory may
   be also set as parameter in the recipe call.

.. attribute:: Recipe.temp_dir

   Base directory for temporary directories where the recipe is executed. The
   working dir is created as a subdir with a random file name. If set to
   :obj:`None`, the system temp dir is used.  Defaults to :literal:`'.'`.

.. attribute:: Recipe.threaded

   Specify whether the recipe should be executed synchroniously or as
   an extra process in the background.

   .. seealso:: :ref:`parallel`

.. autoattribute:: Recipe.tag
.. autoattribute:: Recipe.tags
.. autoattribute:: Recipe.output
.. attribute:: Recipe.memory_dump

   If set to 1, a memory dump is issued to stdout if the memory was
   not totally freed after the execution. If set to 2, the dump is always
   issued. Standard is 0: nothing dumped.

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

Runtime environment
-------------------

For debugging purposes, the runtime environment of the recipe may be
changed. The change may be either done by specifying the :attr:`Recipe.env`
attribute of as a parameter on the recipe invocation. The change will have no
influence on the environment of the framework itself.

.. note::

   Some variables are only read on startup
   (like :envvar:`MALLOC_CHECK_`), changing or deleting them will have
   no effect.

.. autoinstanceattribute:: Recipe.env

   Environment changes for the recipe. This is a :class:`dict` with
   the name of the environment variable as the key and the content as the
   value.  It is possible to overwrite a specific environment
   variable. Specifying :obj:`None` as value will remove the variable::

     >>> muse_flat.env['MUSE_RESAMPLE_LAMBDA_LOG'] = '1'
     >>> muse_flat.env['MUSE_TIMA_FILENAME'] = 'tima.fits'

In a recipe call, the runtime environment may be overwritten as well::

  >>> res = muse_flat( ..., env = {'MUSE_PLOT_TRACE':'true'})

Recipe invocation
-----------------

.. automethod:: Recipe.__call__

.. seealso:: :ref:`parallel`
