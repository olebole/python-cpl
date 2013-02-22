.. _parallel:

Parallel execution
==================

The library allows a simple parallelization of recipe processing. The
parallelization is done using independent processes and thus does not depend
on parallelization features in the CPL or the recipe implementation.

To specify that a recipe should be executed in the background, the
:attr:`threaded` attribute needs to be set to :obj:`True`. This may be done
either in the recipe constructor, as a recipe attribute or as a parameter of
the execution call. Each of the following three recipes will start a
background process for the BIAS calculation::

  # Create a threaded recipe
  r1 = cpl.Recipe('muse_bias', threaded = True)
  result1 = r1([ 'bias1.fits', 'bias2.fits', 'bias3.fits'])

  # Prepare a recipe for background execution
  r2 = cpl.Recipe('muse_bias')
  r2.threaded = True
  result2 = r2([ 'bias1.fits', 'bias2.fits', 'bias3.fits'])

  # Execute a recipe in background
  r3 = cpl.Recipe('muse_bias')
  result3 = r3([ 'bias1.fits', 'bias2.fits', 'bias3.fits'], threaded = True)

If the :attr:`threaded` attribute is set to :obj:`True`, the execution call
of the recipe immediately returns while the recipe is executed in the
background. The current thread is stopped only if any of the results of the
recipe is accessed and the recipe is still not finished.

The result frame of a background recipe is a subclass of
:class:`threading.Thread`. This interface may be used to control the thread
execution.

The simples way to use parallel processing is to create a list where the
members are created by the execution of the recipe. The following example
shows the parallel execution of the 'muse_focus' recipe::

  muse_focus = cpl.Recipe('muse_focus', threaded = True)
  muse_focus.calib.MASTER_BIAS = 'master_bias.fits'

  # Create a list of input files
  files = [ 'MUSE_CUNGC%02i.fits' % i for i in range(20, 30) ]

  # Create a list of recipe results. Note that for each entry, a background
  # process is started.
  results = [ muse_focus(f) for f in files ]

  # Save the results. The current thread is stopped until the according
  # recipe is finished.
  for i, res in enumerate(results):
      res.FOCUS_TABLE.writeto('FOCUS_TABLE_%02i.fits' % (i+1))

When using parallel processing note that the number of parallel processes is
not limited by default, so this feature may produce a high load when called
with a large number of processes. Parallelization in the recipe itself or in
the CPL may also result in additional load.

To limit the maximal number of parallel processes, the function
:func:`cpl.Recipe.set_maxthreads()` can be called with the maximal number of
parallel processes. Note that this function controls only the threads that are
started afterwards.

If the recipe execution fails, the according exception will be raised whenever
one of the results is accessed.

.. note ::

   Recipes may contain an internal parallelization using the `openMP
   <http://openmp.org>`_ interface. Although it is recommended to leave them
   untouched, they may be changed via environment variable settungs in the
   :attr:`cpl.Recipe.env` attribute. See
   http://gcc.gnu.org/onlinedocs/libgomp/Environment-Variables.html for a list
   of environment variables.
