.. module:: cpl

Execution results
=================

Result frames
-------------

.. class:: cpl.Result

   Calling :meth:`cpl.Recipe.__call__` returns an object that contains all
   result ('production') frames in attributes. All results for one tag are
   summarized in one attribute of the same name. So, the ``muse_bias`` recipe
   returns a frame with the tag MASTER_BIAS in the according attribute::
   
     res = muse_bias(...)
     res.MASTER_BIAS.writeto('master_bias')
   
   The attribute content is either a :class:`astropy.io.fits.HDUList` or a
   :func:`list` of HDU lists, depending on the recipe and the call: If the
   recipe produces one out put frame of a tag per input file, the attribute
   contains a list if the recipe was called with a list, and if the recipe was
   called with a single input frame, the result attribute will also contain a
   single input frame. If the recipe combines all input frames to one output
   frame, a single :class:`astropy.io.fits.HDUList` es returned, independent
   of the input parameters. The following examples will illustrate this::
   
     muse_scibasic = cpl.Recipe('muse_scibasic')
     ...
     # Only single input frame, so we get one output frame
     res = muse_scibasic('raw.fits')
     res.PIXTABLE_OBJ.writeto('pixtable.fits')
   
     # List of input frames results in a list of output frames
     res = muse_scibasic([ 'raw1.fits', 'raw2.fits', 'raw3.fits' ])
     for i, h in res.PIXTABLE_OBJ:
         h.writeto('pixtable%i.fits' % (i+1))
   
     # If we call the recipe with a list containing a single frame, we get a list
     # with a single frame back
     res = muse_scibasic([ 'raw1.fits' ])
     res.PIXTABLE_OBJ[0].writeto('pixtable1.fits')
   
     # The bias recipe always returns one MASTER BIAS, regardless of number of
     # input frames. So we always get a single frame back.
     muse_bias = cpl.Recipe('muse_bias')
     ...
     res = muse_bias([ 'bias1.fits', 'bias2.fits', 'bias3.fits' ])
     res.MASTER_BIAS.writeto('master_bias.fits')
   
   .. note:: This works well only for MUSE recipes. Other recipes dont provide
      the necessary information about the recipe.

Run statistics
--------------   

   In Addition to the result frames the :class:`cpl.Result` object provides the
   attribute :attr:`cpl.Result.stat` which contains several statistics of the
   recipe execution:
   
   .. attribute:: cpl.Result.return_code

       The return code of the recipe. Since an exception is thrown if the 
       return code indicates an error, this attribute is always set to 0.

   .. attribute:: cpl.Result.stat.user_time
   
       CPU time in user mode, in seconds.
   
   .. attribute:: cpl.Result.stat.sys_time
   
       CPU time in system mode, in seconds.
   
   .. attribute:: cpl.Result.stat.memory_is_empty
   
       Flag whether the recipe terminated with freeing all available Memory.
       This information is only available if the CPL internal memory
       allocation functions are used. If this information is not available,
       this flag ist set to :obj:`None`.

       .. seealso:: :attr:`Recipe.memory_mode`

Execution log
-------------

   .. attribute:: cpl.Result.log
   
       List of log messages for the recipe.

       .. seealso:: :class:`cpl.logger.LogList`

   .. attribute:: cpl.Result.error

       If one or more error was set during the recipe run, the first error is
       stored in this attribute. The following errors are chained and can be
       accessed with the :attr:`cpl.CplError.next` attribute.  

       .. note:: An error here does not indicate a failed recipe execution,
          since a failed execution would result in a non-zero return code, and
          an exception would be thrown.

       .. seealso:: :class:`cpl.CplError`

Thread control
--------------

   If the recipe was called in the background (see :ref:`parallel`), the result
   object is returned immediately and is dervived from
   :class:`threading.Thread`. Its interface can be used to control the thread
   execution:
   
   .. method:: cpl.Result.isAlive()
   
      Returns whether the recipe is still running
   
   .. method:: cpl.Result.join(timeout = None)
   
      Wait until the recipe terminates. This blocks the calling thread until
      the recipe terminates – either normally or through an unhandled
      exception – or until the optional timeout occurs.
   
      When the timeout argument is present and not :obj:`None`, it should be
      a floating point number specifying a timeout for the operation in
      seconds (or fractions thereof). As :meth:`join` always returns
      :obj:`None`, you must call :meth:`isAlive` after :meth:`join` to decide
      whether a timeout happened – if the recipe is still running, the
      :meth:`join` call timed out.

   When the timeout argument is not present or :obj:`None`, the operation
   will block until the recipe terminates.

   A thread can be :meth:`cpl.Result.join` ed many times. 

   Like in the foreground execution, the output frames may be retrieved as
   attributes of the :class:`cpl.Result` frame. If any of the attributes is
   accessed, the calling thread will block until the recipe is terminated. If
   the recipe execution raised an exception, this exception will be raised
   whenever an attribute is accessed.

CPL Exceptions
--------------
.. autoexception:: CplError

.. autoexception:: RecipeCrash

