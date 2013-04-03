Tutorial
========

Simple example
--------------

The following code takes BIAS input file names from the command line and
writes the MASTER BIAS to the file name provided with the :option:`-o`
option::

  from optparse import OptionParser
  import sys
  import cpl

  parser = OptionParser(usage='%prog files')
  parser.add_option('-o', '--output', help='Output file', default='master_bias.fits')
  parser.add_option('-b', '--badpix-table', help='Bad pixel table')

  (opt, filenames) = parser.parse_args()
  if not filenames:
      parser.print_help()
      sys.exit()

  cpl.esorex.init()

  muse_bias = cpl.Recipe('muse_bias')
  muse_bias.param.nifu = 1
  muse_bias.calib.BADPIX_TABLE = opt.badpix_table

  res = muse_bias(filenames)
  res.MASTER_BIAS.writeto(opt.output)
  
Quick guide
-----------

Input lines are indicated with ">>>" (the python prompt).
The package can be imported with

>>> import cpl

If you migrate from `Esorex <http://www.eso.org/sci/software/cpl/esorex.html>`_, you may just init the search path for CPL recipes
from the esorex startup:

>>> cpl.esorex.init()

Otherwise, you will need to explicitely set the recipe search path:

>>> cpl.Recipe.path = '/store/01/MUSE/recipes'

List available recipes:

>>> cpl.Recipe.list()
[('muse_quick_image', ['0.2.0', '0.3.0']),
 ('muse_scipost', ['0.2.0', '0.3.0']),
 ('muse_scibasic', ['0.2.0', '0.3.0']),
 ('muse_flat', ['0.2.0', '0.3.0']),
 ('muse_subtract_sky', ['0.2.0', '0.3.0']),
 ('muse_bias', ['0.2.0', '0.3.0']),
 ('muse_ronbias', ['0.2.0', '0.3.0']),
 ('muse_fluxcal', ['0.2.0', '0.3.0']),
 ('muse_focus', ['0.2.0', '0.3.0']),
 ('muse_lingain', ['0.2.0', '0.3.0']),
 ('muse_dark', ['0.2.0', '0.3.0']),
 ('muse_combine_pixtables', ['0.2.0', '0.3.0']),
 ('muse_astrometry', ['0.2.0', '0.3.0']),
 ('muse_wavecal', ['0.2.0', '0.3.0']),
 ('muse_exp_combine', ['0.2.0', '0.3.0']),
 ('muse_dar_correct', ['0.2.0', '0.3.0']),
 ('muse_standard', ['0.2.0', '0.3.0']),
 ('muse_create_sky', ['0.2.0', '0.3.0']),
 ('muse_apply_astrometry', ['0.2.0', '0.3.0']),
 ('muse_rebin', ['0.2.0', '0.3.0'])]

Create a recipe specified by name:

>>> muse_scibasic = cpl.Recipe('muse_scibasic')

By default, it loads the recipe with the highest version number. You may also
explicitely specify the version number:

>>> muse_scibasic = cpl.Recipe('muse_scibasic', version = '0.2.0')

List all parameters:

>>> print muse_scibasic.param
{'ybox': 40, 'passes': 2, 'resample': False, 'xbox': 15, 'dlambda': 1.25,
 'cr': 'none', 'thres': 5.8, 'nifu': 0, 'saveimage': True}

Set a parameter:

>>> muse_scibasic.param.nifu = 1

Print the value of a parameter (:obj:`None` if the parameter is set to default)

>>> print muse_scibasic.param.nifu.value
1

List all calibration frames:

>>> print muse_scibasic.calib
{'TRACE_TABLE': None, 'MASTER_SKYFLAT': None, 'WAVECAL_TABLE': None,
 'MASTER_BIAS': None, 'MASTER_DARK': None, 'GEOMETRY_TABLE': None,
 'BADPIX_TABLE': None, 'MASTER_FLAT': None, 'GAINRON_STAT': None}

Set calibration frames with files:

>>> muse_scibasic.calib.MASTER_BIAS    = 'MASTER_BIAS-01.fits'
>>> muse_scibasic.calib.MASTER_FLAT    = 'MASTER_FLAT-01.fits'
>>> muse_scibasic.calib.TRACE_TABLE    = 'TRACE_TABLE-01.fits'
>>> muse_scibasic.calib.GEOMETRY_TABLE = 'geometry_table.fits'

You may also set calibration frames with :class:`astropy.io.fits.HDUList`
objects. This is especially useful if you want to change the file on the fly:

>>> import astropy.io.fits
>>> wavecal = astropy.io.fits.open('WAVECAL_TABLE-01_flat.fits')
>>> wavecal[1].data.field('wlcc00')[:] *= 1.01
>>> muse_scibasic.calib.WAVECAL_TABLE = wavecal

To set more than one file for a tag, put the file names and/or
:class:`astropy.io.fits.HDUList` objects into a list:

>>> muse_scibasic.calib.MASTER_BIAS    = [ 'MASTER_BIAS-%02i.fits' % (i+1) 
...                                        for i in range(24) ]

To run the recipe, call it with the input file names as arguments. The product
frames are returned in the return value of the call. If you don't specify an
input frame tag, the default (first) one of the recipe is used.

>>> res = muse_scibasic('Scene_fusion_1.fits')

Run the recipe with a nondefault tag (use raw data tag as argument name):

>>> res = muse_scibasic(raw = {'SKY':'sky_newmoon_no_noise_1.fits'})

Parameters and calibration frames may be changed for a specific call by
specifying them as arguments:

>>> res =  muse_scibasic('Scene_fusion_1.fits', param = {'nifu': 2}, 
...                      calib = {'MASTER_FLAT': None,
...                               'WAVECAL_TABLE': 'WAVECAL_TABLE_noflat.fits'})

The results of a calibration run are :class:`astropy.io.fits.HDUList` objects.
To save them (use output tags as attributes):

>>> res.PIXTABLE_OBJECT.writeto('Scene_fusion_pixtable.fits')

They can also be used directly as input of other recipes. 

>>> muse_sky = cpl.Recipe('muse_sky')
...
>>> res_sky = muse_sky(res.PIXTABLE_OBJECT)

If not saved, the output is usually lost! During recipe run, a temporary
directory is created where the :class:`astropy.io.fits.HDUList` input objects
and the output files are put into. This directory is cleaned up afterwards.

To control message verbosity on terminal (use :literal:`'debug'`,
:literal:`'info'`, :literal:`'warn'`, :literal:`'error'` or :literal:`'off'`):

>>> cpl.msg.esorex.level = 'debug'

