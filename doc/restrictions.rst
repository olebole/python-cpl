.. _restrictions:

Restrictions for CPL recipes
============================

Not every information can be retrieved from recipes with the standard CPL
functions. Only MUSE recipes provide additional interfaces that allow the
definition of input, calibration and output frames.

All other interfaces will have the following restrictions:

#. The :attr:`cpl.Recipe.calib` attribute is not filled with templates for
   calibration frames. After recipe creation, this attribute is empty. Also, no
   check on the required calibration frames may be done before calling the
   recipe. Anything that is set here will be forwarded to the recipe.

#. In the esorex support, directly assigning the recipe calibration files from
   the SOF file with :literal:`recipe.calib = cpl.esorex.read_sof('{file}')`
   will also put the raw input file into :attr:`Recipe.calib` unless
   :attr:`cpl.Recipe.tags` and/or :attr:`cpl.Recipe.tag` are set
   manually. The standard recipe interface does not provide a way to
   distinguish between raw input and calibration files.

#. The ``TAG=frame`` options in the recipe call cannot be used.

#. The :attr:`cpl.Recipe.tags` attribute is set to None.

#. The :attr:`cpl.Recipe.tag` attribute is not initially set. If this attribute is
   not set manually, the tag is required when executing the attribute.

#. The method :meth:`cpl.Recipe.output` raises an exception.

Technical Background
--------------------

CPL recipes register all their parameter definitions with the CPL function
:func:`cpl_parameterlist_append()`. All registeres parameters may be retrieved
from the recipe structure as a structure which contains all defined
parameters.

For frames, such a mechanism does not exist, although components of the
infrastructure are implemented. The CPL modules :mod:`cpl_recipeconfig` allows
the definition of input, raw, and output frames for a recipe. However, this
module is only half-way done, has no connection to the recipe definition and
is not mandantory for CPL recipes. The MUSE pipeline recipes (with the
exception of those contributed by ESO) implement a central frameconfig
registry which allows to access this meta information from the Python
interface.

The situation here is quite unsatisfying. ESO states that 

- the CPL is single-purpose for the standard non-interactive recipe processing, 

- further usability (especially interactive use and debugging) is not on their
  scope, and

- they have no interest in supporting Python.

