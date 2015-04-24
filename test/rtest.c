/*
 * Copyright (C) 2002,2003 European Southern Observatory
 * Copyright (C) 2011-2015 Ole Streicher
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <string.h>
#include <cpl.h>

#if ( CPL_VERSION_CODE < CPL_VERSION(6,3,0))
#define cpl_frameset_get_position cpl_frameset_get_frame
#endif

#define RRRECIPE_RAW                    "RRRECIPE_DOCATG_RAW"
#define IIINSTRUMENT_CALIB_FLAT         "FLAT"

static int rtest_create(cpl_plugin *);
static int rtest_exec(cpl_plugin *);
static int rtest_destroy(cpl_plugin *);
static int rtest(cpl_frameset *, const cpl_parameterlist *);

static char rtest_description[] =
"Recipe to test CPL frameworks like esorex or python-cpl.\n";
static char *license = "GPL";

/**
  @brief    Set the group as RAW or CALIB in a frameset
  @param    set     the input frameset
  @return   CPL_ERROR_NONE iff OK
 */
cpl_error_code dfs_set_groups(cpl_frameset * set)
{
    cpl_errorstate prestate = cpl_errorstate_get();
    cpl_frame * frame = NULL;
    int i = 0;
    int n = cpl_frameset_get_size(set);

    /* Loop on frames */
    for (i = 0; i < n; i++) {
	frame = cpl_frameset_get_position(set, i);
        const char * tag = cpl_frame_get_tag(frame);

        if (tag == NULL) {
            cpl_msg_warning(cpl_func, "Frame %d has no tag", i);
        } else if (!strcmp(tag, RRRECIPE_RAW)) {
            /* RAW frames */
            cpl_frame_set_group(frame, CPL_FRAME_GROUP_RAW);
        } else if (!strcmp(tag, IIINSTRUMENT_CALIB_FLAT)) {
            /* CALIB frames */
            cpl_frame_set_group(frame, CPL_FRAME_GROUP_CALIB);
        }
    }

    if (!cpl_errorstate_is_equal(prestate)) {
        return cpl_error_set_message(cpl_func, cpl_error_get_code(),
                                     "Could not identify RAW and CALIB "
                                     "frames");
    }

    return CPL_ERROR_NONE;
}

/**
  @brief    find out the DIT value 
  @param    plist       property list to read from
  @return   the requested value
 */
static double pfits_get_dit(const cpl_propertylist * plist)
{
    cpl_errorstate prestate = cpl_errorstate_get();
    const double value = cpl_propertylist_get_double(plist, "ESO DET DIT");

    /* Check for a change in the CPL error state */
    /* - if it did change then propagate the error and return */
    cpl_ensure(cpl_errorstate_is_equal(prestate), cpl_error_get_code(), 0.0);

    return value;
}

/**
  @brief    Build the list of available plugins, for this module.
  @param    list    the plugin list
  @return   0 if everything is ok, 1 otherwise
  @note     Only this function is exported

  Create the recipe instance and make it available to the application using the
  interface.
 */
int cpl_plugin_get_info(cpl_pluginlist * list)
{
    cpl_recipe  *   recipe = cpl_calloc(1, sizeof *recipe );
    cpl_plugin  *   plugin = &recipe->interface;

    if (cpl_plugin_init(plugin,
		    CPL_PLUGIN_API,
		    1,
		    CPL_PLUGIN_TYPE_RECIPE,
		    "rtest",
		    "Framework test recipe",
		    rtest_description,
		    "Ole Streicher",
		    "python-cpl@liska.ath.cx",
		    license,
		    rtest_create,
		    rtest_exec,
		    rtest_destroy)) {
	cpl_msg_error(cpl_func, "Plugin initialization failed");
	(void)cpl_error_set_where(cpl_func);
	return 1;
    }

    if (cpl_pluginlist_append(list, plugin)) {
	cpl_msg_error(cpl_func, "Error adding plugin to list");
	(void)cpl_error_set_where(cpl_func);
	return 1;
    }

    return 0;
}

/**
  @brief    Setup the recipe options
  @param    plugin  the plugin
  @return   0 if everything is ok

  Defining the command-line/configuration parameters for the recipe.
 */
static int rtest_create(cpl_plugin * plugin)
{
    cpl_ensure_code((plugin != NULL), CPL_ERROR_NULL_INPUT);
    cpl_ensure_code((cpl_plugin_get_type(plugin) == CPL_PLUGIN_TYPE_RECIPE),
		    CPL_ERROR_TYPE_MISMATCH);

    cpl_recipe *recipe = (cpl_recipe *)plugin;

    /* Create the parameters list in the cpl_recipe object */
    recipe->parameters = cpl_parameterlist_new();
    if (recipe->parameters == NULL) {
	cpl_msg_error(cpl_func, "Parameter list allocation failed");
	cpl_ensure_code(0, (int)CPL_ERROR_ILLEGAL_OUTPUT);
    }

    /* Fill the parameters list */
    cpl_parameter * p;
    /* --stropt */
    p = cpl_parameter_new_value("iiinstrument.rtest.string_option",
	    CPL_TYPE_STRING,
	    "A string option; saved as ESO QC STROPT",
	    "iiinstrument.rtest",NULL);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "stropt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --boolopt */
    p = cpl_parameter_new_value("iiinstrument.rtest.bool_option",
	    CPL_TYPE_BOOL,
	    "A flag; saved as ESO QC BOOLOPT",
	    "iiinstrument.rtest", TRUE);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "boolopt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --floatopt */
    p = cpl_parameter_new_value("iiinstrument.rtest.float_option",
	    CPL_TYPE_DOUBLE,
	    "A double option; saved as ESO QC FLOATOPT",
	    "iiinstrument.rtest", 0.1);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "floatopt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --inttopt */
    p = cpl_parameter_new_value("iiinstrument.rtest.int_option",
	    CPL_TYPE_INT,
	    "An interger; saved as ESO QC INTOPT",
	    "iiinstrument.rtest", 2);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "intopt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --enumopt */
    p = cpl_parameter_new_enum("iiinstrument.rtest.enum_option",
	    CPL_TYPE_STRING,
	    "An enumeration option, saved as ESO QC ENUMOPT",
	    "iiinstrument.rtest", "first", 3, "first", "second", "third");
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "enumopt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --rangeopt */
    p = cpl_parameter_new_range("iiinstrument.rtest.range_option",
	    CPL_TYPE_DOUBLE,
	    "A double option with a range, saved as ESO QC RANGEOPT",
	    "iiinstrument.rtest", 0.1, -0.5, 0.5);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "rangeopt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --dot.opt */
    p = cpl_parameter_new_value("iiinstrument.rtest.dotted.opt",
	    CPL_TYPE_INT,
	    "An (integer) option with a dot in its name",
	    "iiinstrument.rtest", 0);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "dot.opt");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --crashing */
    p = cpl_parameter_new_enum("iiinstrument.rtest.crashing",
	  CPL_TYPE_STRING, "Crash the recipe?", "iiinstrument.rtest",
			       "no", 3, "no", "free", "segfault");
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "crashing");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --memleak */
    p = cpl_parameter_new_value("iiinstrument.rtest.memleak",
	    CPL_TYPE_BOOL,
	    "If yes, dont deallocate some memory",
	    "iiinstrument.rtest", FALSE);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "memleak");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --sleep */
    p = cpl_parameter_new_value("iiinstrument.rtest.sleep",
	    CPL_TYPE_DOUBLE,
	    "Simulate some computing by sleeping for specified time [seconds]",
	    "iiinstrument.rtest", 0.1);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "sleep");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameterlist_append(recipe->parameters, p);

    /* --disabled */
    p = cpl_parameter_new_value("iiinstrument.rtest.disabled",
	    CPL_TYPE_DOUBLE,
	    "Dummy disabled parameter",
	    "iiinstrument.rtest", -0.1);
    cpl_parameter_set_alias(p, CPL_PARAMETER_MODE_CLI, "disabled");
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_ENV);
    cpl_parameter_disable(p, CPL_PARAMETER_MODE_CLI);
    cpl_parameterlist_append(recipe->parameters, p);

    return 0;
}

/**
  @brief    Execute the plugin instance given by the interface
  @param    plugin  the plugin
  @return   0 if everything is ok
 */
static int rtest_exec(cpl_plugin * plugin)
{
    cpl_ensure_code((plugin != NULL), CPL_ERROR_NULL_INPUT);
    cpl_ensure_code((cpl_plugin_get_type(plugin) == CPL_PLUGIN_TYPE_RECIPE),
		    CPL_ERROR_TYPE_MISMATCH);

    cpl_recipe *recipe = (cpl_recipe *)plugin;

    cpl_ensure_code((recipe->parameters != NULL), (int)CPL_ERROR_NULL_INPUT);
    cpl_ensure_code((recipe->frames != NULL), (int)CPL_ERROR_NULL_INPUT);

    int recipe_status = rtest(recipe->frames, recipe->parameters);

    /* Ensure DFS-compliance of the products */
    if (cpl_dfs_update_product_header(recipe->frames)) {
	if (!recipe_status) recipe_status = (int)cpl_error_get_code();
    }

    return recipe_status;
}

/**
  @brief    Destroy what has been created by the 'create' function
  @param    plugin  the plugin
  @return   0 if everything is ok
 */
static int rtest_destroy(cpl_plugin * plugin)
{
    cpl_ensure_code((plugin != NULL), CPL_ERROR_NULL_INPUT);
    cpl_ensure_code((cpl_plugin_get_type(plugin) == CPL_PLUGIN_TYPE_RECIPE),
		    CPL_ERROR_TYPE_MISMATCH);

    cpl_recipe *recipe = (cpl_recipe *)plugin;
    cpl_parameterlist_delete(recipe->parameters);

    return 0;
}

/**
  @brief    Interpret the command line options and execute the data processing
  @param    frameset   the frames list
  @param    parlist    the parameters list
  @return   0 if everything is ok
 */
static int rtest(cpl_frameset            * frameset,
		    const cpl_parameterlist * parlist)
{
    /* Use the errorstate to detect an error in a function that does not
       return an error code. */
    cpl_errorstate prestate = cpl_errorstate_get();

    const cpl_parameter *param;
    /* --stropt */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.string_option");
    const char *str_option = cpl_parameter_get_string(param);
    cpl_ensure_code(str_option != NULL, CPL_ERROR_NULL_INPUT);

    /* --boolopt */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.bool_option");
    int bool_option = cpl_parameter_get_bool(param);

    /* --floatopt */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.float_option");
    double float_option = cpl_parameter_get_double(param);

    /* --intopt */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.int_option");
    int int_option = cpl_parameter_get_int(param);

    /* --enumopt */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.enum_option");
    const char *enum_option = cpl_parameter_get_string(param);

    /* --rangeopt */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.range_option");
    double range_option = cpl_parameter_get_double(param);

    /* --crashing */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.crashing");
    const char *crashing = cpl_parameter_get_string(param);

    /* --memleak */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.memleak");
    int memleak = cpl_parameter_get_bool(param);

    /* --sleep */
    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.sleep");
    double sleep_secs = cpl_parameter_get_double(param);

    param = cpl_parameterlist_find_const(parlist,
					 "iiinstrument.rtest.disabled");
    double disabled_option = cpl_parameter_get_double(param);

    if (!cpl_errorstate_is_equal(prestate)) {
	return (int)cpl_error_set_message(cpl_func, cpl_error_get_code(),
					  "Could not retrieve the input "
					  "parameters");
    }

    /* Identify the RAW and CALIB frames in the input frameset */
    cpl_ensure_code(dfs_set_groups(frameset) == CPL_ERROR_NONE,
		    cpl_error_get_code());

    /*  - raw input file */
    const cpl_frame *rawframe = cpl_frameset_find_const(frameset, RRRECIPE_RAW);
    if (rawframe == NULL) {
	/* cpl_frameset_find_const() does not set an error code, when a frame
	   is not found, so we will set one here. */
	return (int)cpl_error_set_message(cpl_func, CPL_ERROR_DATA_NOT_FOUND,
					  "No file tagged with %s", RRRECIPE_RAW);
    }

    cpl_propertylist *plist
	= cpl_propertylist_load_regexp(cpl_frame_get_filename(rawframe),
				       0, "ESO DET ", 0);
    if (plist == NULL) {
	/* In this case an error message is added to the error propagation */
	cpl_msg_error(cpl_func, "Could not read plist from %s",
		      cpl_frame_get_filename(rawframe));
	return (int)cpl_error_set_message(cpl_func, cpl_error_get_code(),
					  "Could not read the FITS header");
    }

    double qc_param = pfits_get_dit(plist);
    cpl_errorstate_set(prestate);

    cpl_propertylist_delete(plist);

    /* - calibration input file */
    const cpl_frame *flat = cpl_frameset_find(frameset,IIINSTRUMENT_CALIB_FLAT);
    if (flat == NULL) {
	cpl_msg_warning(cpl_func, "No file tagged with %s",
			IIINSTRUMENT_CALIB_FLAT);
    }

    /* Check for a change in the CPL error state */
    /* - if it did change then propagate the error and return */
    cpl_ensure_code(cpl_errorstate_is_equal(prestate), cpl_error_get_code());

    /* Load raw image */
    cpl_image *image = cpl_image_load(cpl_frame_get_filename(rawframe),
				      CPL_TYPE_FLOAT, 0, 0);

    /* A multiline debug message */
    cpl_msg_info(cpl_func, "multiline#1\nmultiline#2\nmultiline#3");

    /* Do some fake processing */
    usleep((unsigned int)(1e6*sleep_secs));

    /* Add QC parameters  */
    cpl_propertylist *qclist = cpl_propertylist_new();

    cpl_propertylist_append_double(qclist, "ESO QC QCPARAM", qc_param);
    cpl_propertylist_append_string(qclist, "ESO PRO CATG","THE_PRO_CATG_VALUE");
    if (str_option != NULL) {
	cpl_propertylist_append_string(qclist, "ESO QC STROPT", str_option);
    } else {
	cpl_propertylist_append_string(qclist, "ESO QC STROPT", "(null)");
    }

    cpl_propertylist_append_bool(qclist, "ESO QC BOOLOPT", bool_option);
    cpl_propertylist_append_double(qclist, "ESO QC FLOATOPT", float_option);
    cpl_propertylist_append_int(qclist, "ESO QC INTOPT", int_option);
    if (enum_option != NULL) {
	cpl_propertylist_append_string(qclist, "ESO QC ENUMOPT", enum_option);
    } else {
	cpl_propertylist_append_string(qclist, "ESO QC ENUMOPT", "(null)");
    }
    cpl_propertylist_append_double(qclist, "ESO QC RANGEOPT", range_option);
    const char *testenv = getenv("TESTENV");
    if (testenv != NULL) {
	cpl_propertylist_append_string(qclist, "ESO QC TESTENV", testenv);
    } else {
	cpl_propertylist_append_string(qclist, "ESO QC TESTENV", "(null)");
    }
    cpl_propertylist_append_double(qclist, "ESO QC DISABLEDOPT", disabled_option);

    prestate = cpl_errorstate_get();

    if (cpl_dfs_save_image(frameset, NULL, parlist, frameset, NULL, image,
			   CPL_BPP_IEEE_FLOAT,
			   "rtest", qclist, NULL,
			   "iiinstrument/0.0.1",
			   "rtest.fits")) {
	/* Propagate the error */
	(void)cpl_error_set_where(cpl_func);
    }

    if (!cpl_errorstate_is_equal(prestate)) {
	cpl_msg_error(__func__, "in cpl_dfs_save_image()");
    }

    cpl_image_delete(image);
    cpl_propertylist_delete(qclist);

    /* Let's see if we can crash the machine by some random code */
    if (strcmp(crashing, "free") == 0) {
	cpl_image_delete(image);
	cpl_propertylist_delete(qclist);
    }
    if (strcmp(crashing, "segfault") == 0) {
	double *crashvar = NULL;
	*crashvar = 1.99;
    }

    if (memleak) {
	__attribute__((unused))	void * r = cpl_malloc(16);
    }

    return (int)cpl_error_get_code();
}
