#include <Python.h>
#include <unistd.h>
#include <dlfcn.h>
#include <sys/wait.h>
#include <sys/times.h>
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#ifdef linux
#include <sys/prctl.h>
#define HAVE_PRCTL
#include <mcheck.h>
#define HAVE_MCHECK
#define HAVE_MTRACE
#include <malloc.h>
#define HAVE_MALLOPT
#endif

/* Define PY_Type for Python <= 2.6 */
#ifndef Py_TYPE
    #define Py_TYPE(ob) (((PyObject*)(ob))->ob_type)
#endif
#ifndef PyVarObject_HEAD_INIT
    #define PyVarObject_HEAD_INIT(type, size) \
        PyObject_HEAD_INIT(type) size,
#endif

#include "CPL_library.h"

#define CPL_list_doc \
    "List all CPL recipe names contained in a shared library."

static PyObject *
CPL_list(PyObject *self, PyObject *args) {
    const char *file;

    if (!PyArg_ParseTuple(args, "s", &file))
        return NULL;

    void *handle = dlopen(file, RTLD_LAZY);
    if (handle == NULL) {
	Py_INCREF(Py_None);
	return Py_None;
    }

    char *error =dlerror();
    int (*cpl_plugin_get_info)(cpl_pluginlist *) = dlsym(handle,
							 "cpl_plugin_get_info");
    error = dlerror();
    if (error != NULL)  {
	dlclose(handle);
	Py_INCREF(Py_None);
	return Py_None;
    }

    cpl_library_t *cpl = create_library(file);
    PyObject *res = PyList_New(0);
    Py_INCREF(res);
    cpl_pluginlist *list = cpl->pluginlist_new();
    (*cpl_plugin_get_info)(list);
    cpl_plugin *plugin;
    for (plugin = cpl->pluginlist_get_first(list);
	 plugin != NULL;
	 plugin = cpl->pluginlist_get_next(list)) {
	cpl->error_reset();
	cpl->plugin_get_init(plugin)(plugin);
	char *version = cpl->plugin_get_version_string(plugin);
	PyList_Append(res, Py_BuildValue("sis", 
					 cpl->plugin_get_name(plugin),
					 cpl->plugin_get_version(plugin),
					 version));
	cpl->free(version);
	cpl->plugin_get_deinit(plugin)(plugin);
    }
    cpl->pluginlist_delete(list);
    cpl->error_reset();
    dlclose(handle);
    return res;
}

#define CPL_supported_versions_doc \
    "List all supported CPL versions."

static PyObject *
CPL_supported_versions(PyObject *self, PyObject *args) {
    PyObject *res = PyList_New(0);
    Py_INCREF(res);
    int i;
    for (i = 0; supported_versions[i] != 0; i++) {
	PyList_Append(res, Py_BuildValue(
			  "iii", 
			  CPL_VERSION_MAJOR_CODE(supported_versions[i]),
			  CPL_VERSION_MINOR_CODE(supported_versions[i]),
			  CPL_VERSION_MICRO_CODE(supported_versions[i])));
    }
    return res;
}

static PyMethodDef CPL_methods[] = {
    {"list", CPL_list, METH_VARARGS, CPL_list_doc},
    {"cpl_versions", CPL_supported_versions, METH_NOARGS, 
     CPL_supported_versions_doc},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

typedef struct {
    PyObject_HEAD
    cpl_plugin *plugin;
    cpl_pluginlist *pluginlist;
    void *handle;
    cpl_recipeconfig *recipeconfig;
    cpl_library_t *cpl;
} CPL_recipe;

static void
CPL_recipe_dealloc(CPL_recipe* self) {
    if (self->plugin != NULL) {
	self->cpl->plugin_get_deinit(self->plugin)(self->plugin);
    }
    if (self->pluginlist != NULL) {
	self->cpl->pluginlist_delete(self->pluginlist);
    }
    if (self->handle != NULL) {
	dlclose(self->handle);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
CPL_recipe_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    CPL_recipe *self = (CPL_recipe *)type->tp_alloc(type, 0);
    if (self != NULL) {
	self->plugin = NULL;
	self->pluginlist = NULL;
	self->handle = NULL;
	self->recipeconfig = NULL;
	self->cpl = NULL;
    }
    return (PyObject *)self;
}

#define CPL_recipe_doc                \
    "Raw CPL recipe object.\n\n"      \
    "Constructor parameters:\n"       \
    " - shared library file name\n"   \
    " - recipe name\n"

static int
CPL_recipe_init(CPL_recipe *self, PyObject *args, PyObject *kwds) {
    const char *file;
    const char *recipe;
    if (!PyArg_ParseTuple(args, "ss", &file, &recipe))
        return -1;
    
    self->handle = dlopen(file, RTLD_LAZY);
    if (self->handle == NULL) {
	PyErr_SetString(PyExc_IOError, "cannot open shared library");
	return -1;
    }
    dlerror();
    int (*cpl_plugin_get_info)(cpl_pluginlist *) 
	= dlsym(self->handle, "cpl_plugin_get_info");
    char *error = dlerror();
    if (error != NULL)  {
	PyErr_SetString(PyExc_IOError, error);
	return -1;
    }

    self->cpl = create_library(file);
    self->cpl->error_reset();
    self->pluginlist = self->cpl->pluginlist_new();
    (*cpl_plugin_get_info)(self->pluginlist);
    self->plugin = self->cpl->pluginlist_find(self->pluginlist, recipe);
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "cannot find recipe in shared library");
	return -1;
    } else {
	self->cpl->plugin_get_init(self->plugin)(self->plugin);
    }
    
    if (self->cpl->get_recipeconfig != NULL) {
	self->recipeconfig = self->cpl->get_recipeconfig((cpl_recipe *)self->plugin);
    } else {
	self->recipeconfig = NULL;
    }
    return 0;
}

#define CPL_is_supported_doc \
    "Check whether the CPL version is supported by python-cpl."

static PyObject *
CPL_is_supported(CPL_recipe *self) {
    return (self->cpl->is_supported == UNKNOWN_VERSION)?Py_False:Py_True;
}

#define CPL_version_doc \
    "Get the CPL version string."

static PyObject *
CPL_version(CPL_recipe *self) {
    return Py_BuildValue("s", self->cpl->version_get_version());
}

#define CPL_description_doc \
    "Get the string of version numbers of CPL and its libraries."

static PyObject *
CPL_description(CPL_recipe *self) {
    return Py_BuildValue("s", self->cpl->get_description(CPL_DESCRIPTION_DEFAULT));
}

static PyObject *
getParameter(CPL_recipe *self, cpl_parameter *param) {
    cpl_type type = self->cpl->parameter_get_type(param);
    cpl_parameter_class class = self->cpl->parameter_get_class(param);
    const char *name = self->cpl->parameter_get_alias(param, 
					       CPL_PARAMETER_MODE_CLI);
    const char *fullname = self->cpl->parameter_get_name(param);
    const char *context = self->cpl->parameter_get_context(param);
    const char *help = self->cpl->parameter_get_help(param);
    PyObject *range = Py_None;
    if (class == CPL_PARAMETER_CLASS_RANGE) {
	if (type == self->cpl->TYPE_INT) {
	    range = Py_BuildValue("ii",
				  self->cpl->parameter_get_range_min_int(param),
				  self->cpl->parameter_get_range_max_int(param));
	} else if (type == self->cpl->TYPE_DOUBLE) {
	    range = Py_BuildValue("dd",
				  self->cpl->parameter_get_range_min_double(param),
				  self->cpl->parameter_get_range_max_double(param));
	}
    }
    Py_INCREF(range);
    PyObject *sequence = Py_None;
    if (class == CPL_PARAMETER_CLASS_ENUM) {
	sequence = PyList_New(0);
	int n_enum = self->cpl->parameter_get_enum_size(param);
	int i;
	for (i = 0; i < n_enum; i++) {
	    if (type == self->cpl->TYPE_INT) {
		PyList_Append(
		    sequence, 
		    Py_BuildValue("i",
				  self->cpl->parameter_get_enum_int(param, i)));
	    } else if (type == self->cpl->TYPE_DOUBLE) {
		PyList_Append(
		    sequence, 
		    Py_BuildValue("d",
				  self->cpl->parameter_get_enum_double(param, i)));
	    } else if (type == self->cpl->TYPE_STRING) {
		PyList_Append(
		    sequence, 
		    Py_BuildValue("s",
				  self->cpl->parameter_get_enum_string(param, i)));
	    }
	}
    }
    Py_INCREF(sequence);
    PyObject *deflt = Py_None;
    PyObject *ptype = Py_None;
    if (type == self->cpl->TYPE_BOOL) {
	ptype = (PyObject *)&PyBool_Type;
	deflt = (self->cpl->parameter_get_default_bool(param))?Py_True:Py_False;
    } else if (type == self->cpl->TYPE_INT) {
	ptype = (PyObject *)&PyLong_Type;
	deflt = Py_BuildValue("i", self->cpl->parameter_get_default_int(param));
    } else if (type == self->cpl->TYPE_DOUBLE) {
	ptype = (PyObject *)&PyFloat_Type;
	deflt = Py_BuildValue("d", self->cpl->parameter_get_default_double(param));
    } else if (type == self->cpl->TYPE_STRING) {
#if PY_MAJOR_VERSION < 3
	ptype = (PyObject *)&PyString_Type;
#else
	ptype = (PyObject *)&PyUnicode_Type;
#endif
	deflt = Py_BuildValue("s", self->cpl->parameter_get_default_string(param));
    }
    Py_INCREF(deflt);
    Py_INCREF(ptype);
    PyObject *enabled = Py_BuildValue(
	"OOO",
	self->cpl->parameter_is_enabled(param, CPL_PARAMETER_MODE_CLI)?Py_True:Py_False,
	self->cpl->parameter_is_enabled(param, CPL_PARAMETER_MODE_ENV)?Py_True:Py_False,
	self->cpl->parameter_is_enabled(param, CPL_PARAMETER_MODE_CFG)?Py_True:Py_False);
    Py_INCREF(enabled);

    PyObject *par = Py_BuildValue("ssssNNNNN",
				  name, context, fullname, help,
				  range, sequence, deflt, ptype,
				  enabled);
    Py_INCREF(par);
    return par;
}


#define CPL_recipe_get_params_doc                                          \
    "Get the possible parameters.\n\n"                                     \
    "Returns a list of tuples where each tuple defines one parameter:\n"   \
    " - parameter name\n"                                                  \
    " - parameter context\n"                                               \
    " - description\n"                                                     \
    " - range (min, max), if valid range is limited, or None\n"            \
    " - allowed values, if only certain values are allowed, or None\n"     \
    " - default value\n"                                                   \
    " - triple (cli, env, cfg) with enabled-values for param modes"

static PyObject *
CPL_recipe_get_params(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    cpl_parameterlist *pars = ((cpl_recipe *)self->plugin)->parameters;
    PyObject *res = PyList_New(0);
    if (pars && self->cpl->parameterlist_get_size(pars)) {
	cpl_parameter *param;
	for (param = self->cpl->parameterlist_get_first(pars);
	     param != NULL;  
	     param = self->cpl->parameterlist_get_next(pars)) {
	    PyList_Append(res, getParameter(self, param));
	}
    }
    Py_INCREF(res);
    return res;
}

#define CPL_recipe_get_author_doc                                        \
    "Get the author and his email.\n\n"                                  \
    "Returns a pair where the first field is the author name and the\n"  \
    "second field is the E-mail address."

static PyObject *
CPL_recipe_get_author(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    return Py_BuildValue("ss", 
			 self->cpl->plugin_get_author(self->plugin),
			 self->cpl->plugin_get_email(self->plugin));
}

#define CPL_recipe_get_description_doc                                      \
    "Get the synopsis and description.\n\n"                                 \
    "Returns a pair where the first field is the synopsis string and the\n" \
    "second field is the description string."

static PyObject *
CPL_recipe_get_description(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    return Py_BuildValue("ss", 
			 self->cpl->plugin_get_synopsis(self->plugin),
			 self->cpl->plugin_get_description(self->plugin));
}

#define CPL_recipe_get_version_doc                                            \
    "Get the version as integer and string.\n\n"                              \
    "Returns a pair where the first entry is the version number as integer\n" \
    "and the second entry is the version string.\n"

static PyObject *
CPL_recipe_get_version(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    return Py_BuildValue("is", 
			 self->cpl->plugin_get_version(self->plugin),
			 self->cpl->plugin_get_version_string(self->plugin));
}

#define CPL_recipe_get_copyright_doc                                          \
    "Get the license and copyright information."

static PyObject *
CPL_recipe_get_copyright(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    return Py_BuildValue("s", 
			 self->cpl->plugin_get_copyright(self->plugin));
}

#define CPL_recipe_get_frameconfig_doc                                        \
    "Get the possible frame configurations.\n\n"                              \
    "Returns a list of tuples. Each tupel is the frame configuration of one\n"\
    "input frame tag. It consists of\n"                                       \
    " - input frame configuration (tupel with tag, minimal and maximal\n"     \
    "   number of frames\n"                                                   \
    " - list of configuration frames (each is a tupel with tag, minimal and\n"\
    "   maximal number of frames)\n"                                          \
    " - list of output tags\n"                                                \
    "Unset minimum/maximum values are indicated by -1"

static PyObject *
CPL_recipe_get_frameconfig(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    if (self->recipeconfig == NULL) {
	Py_INCREF(Py_None);
	return Py_None;
    }
    PyObject *res = PyList_New(0);
    char **tags = self->cpl->recipeconfig_get_tags(self->recipeconfig);
    int i_tag;
    for (i_tag = 0; tags[i_tag] != NULL; i_tag++) {
	int min = self->cpl->recipeconfig_get_min_count(self->recipeconfig,
						 tags[i_tag], tags[i_tag]);
	int max = self->cpl->recipeconfig_get_max_count(self->recipeconfig,
						 tags[i_tag], tags[i_tag]);
	PyObject *raw = Py_BuildValue("sii", tags[i_tag], min, max);
	PyObject *calib = PyList_New(0);

	char **inputs = self->cpl->recipeconfig_get_inputs(self->recipeconfig,
						    tags[i_tag]);
	int i_input;
	for (i_input = 0; inputs[i_input] != NULL; i_input++) {
	    int min = self->cpl->recipeconfig_get_min_count(self->recipeconfig,
						     tags[i_tag], 
						     inputs[i_input]);
	    int max = self->cpl->recipeconfig_get_max_count(self->recipeconfig,
						     tags[i_tag], 
						     inputs[i_input]);
	    PyList_Append(calib, Py_BuildValue("sii", inputs[i_input], 
					       min, max));
	    self->cpl->free(inputs[i_input]);
	}
	self->cpl->free(inputs);

	PyObject *output = PyList_New(0);
	char **outputs = self->cpl->recipeconfig_get_outputs(self->recipeconfig,
						      tags[i_tag]);
	int i_output;
	for (i_output = 0; outputs[i_output] != NULL; i_output++) {
	    PyList_Append(output, Py_BuildValue("s", outputs[i_output]));
	    self->cpl->free(outputs[i_output]);
	}
	self->cpl->free(outputs);
	
	PyList_Append(res, Py_BuildValue("OOO", raw, calib, output));
	
	self->cpl->free(tags[i_tag]);
    }
    self->cpl->free(tags);
    return res;
}

static cpl_frameset *
get_frames(CPL_recipe *self, PyObject *framelist) {
    cpl_frameset *frames = self->cpl->frameset_new();
    PyObject *iter = PyObject_GetIter(framelist);
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
	const char *tag;
	const char* file;
	PyArg_ParseTuple(item, "ss", &tag, &file);
	cpl_frame *frame = self->cpl->frame_new();
	self->cpl->frame_set_filename(frame, file);
	self->cpl->frame_set_tag(frame, tag);
	self->cpl->frameset_insert(frames, frame);
	Py_DECREF(item);
    }
    Py_DECREF(iter);
    return frames;
}

static void 
clear_parameters(CPL_recipe *self, cpl_parameterlist *parameters) {
    cpl_parameter *par = self->cpl->parameterlist_get_first(parameters);
    while (par != NULL) {
	cpl_type type = self->cpl->parameter_get_type(par);
	if (type == self->cpl->TYPE_STRING) {
	    const char *default_value = self->cpl->parameter_get_default_string(par);
	    if (default_value == NULL) {
		default_value = "";
	    }
	    self->cpl->parameter_set_string(par, default_value);
	} else if (type == self->cpl->TYPE_INT) {
	    self->cpl->parameter_set_int(par, 
				 self->cpl->parameter_get_default_int(par));
	} else if (type == self->cpl->TYPE_DOUBLE) {
	    self->cpl->parameter_set_double(par, 
				 self->cpl->parameter_get_default_double(par));
	} else if (type == self->cpl->TYPE_BOOL) {
	    self->cpl->parameter_set_bool(par, 
				 self->cpl->parameter_get_default_bool(par));
	}
	
	par = self->cpl->parameterlist_get_next(parameters);
    }
    
}

static void
set_parameters(CPL_recipe *self, cpl_parameterlist *parameters, PyObject *parlist) {
    PyObject *iter = PyObject_GetIter(parlist);
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
	const char *name;
	PyObject *value;
	PyArg_ParseTuple(item, "sO", &name, &value);
	cpl_parameter *par = self->cpl->parameterlist_find(parameters, name);
	if (par == NULL) {
	    continue;
	}
	cpl_type type = self->cpl->parameter_get_type(par);
	if (type == self->cpl->TYPE_STRING) {
#if PY_MAJOR_VERSION < 3
	    if (PyString_Check(value)) {
		self->cpl->parameter_set_string(par, PyString_AsString(value));
	    }
#else
	    if (PyUnicode_Check(value)) {
		PyObject* temp = PyUnicode_AsASCIIString(value);
		if (temp != NULL) {
		    self->cpl->parameter_set_string(par,
						    PyBytes_AsString(temp));
		    Py_XDECREF(temp);
		}
	    }
#endif
	} else if (type == self->cpl->TYPE_INT) {
	    if (PyLong_Check(value)) {
		self->cpl->parameter_set_int(par, PyLong_AsLong(value));
	    }
	} else if (type == self->cpl->TYPE_DOUBLE) {
	    if (PyFloat_Check(value)) {
		self->cpl->parameter_set_double(par, PyFloat_AsDouble(value));
	    }
	} else if (type == self->cpl->TYPE_BOOL) {
	    self->cpl->parameter_set_bool(par, PyObject_IsTrue(value));
	}
	Py_DECREF(item);
    }
    Py_DECREF(iter);
}

static void
set_environment(PyObject *runenv) {
    PyObject *iter = PyObject_GetIter(runenv);
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
	const char *name;
	PyObject *value;
	PyArg_ParseTuple(item, "sO", &name, &value);
	if ((name == NULL) || (value == NULL)) {
	    continue;
	}
#if PY_MAJOR_VERSION < 3
	if (PyString_Check(value)) {
	    setenv(name, PyString_AsString(value), 1);
	}
#else
	    if (PyUnicode_Check(value)) {
		PyObject* temp = PyUnicode_AsASCIIString(value);
		if (temp != NULL) {
		    setenv(name, PyBytes_AsString(temp), 1);
		    Py_XDECREF(temp);
		}
	    }
#endif
	if (value == Py_None) {
	    unsetenv(name);
	}
	Py_DECREF(item);
    }
    Py_DECREF(iter);
}

static PyObject *
exec_build_retval(void *ptr) {
    long ret_code = ((long *)ptr)[1];
    double user_time = ((long *)ptr)[2] * 1e-6;
    double sys_time = ((long *)ptr)[3] * 1e-6;
    int memcheck = ((long *)ptr)[4];
    PyObject *stats = Py_BuildValue("iffi", 
				    ret_code, user_time, sys_time, memcheck);

    long n_errors = ((long *)ptr)[5];

    long index = 6 * sizeof(long);
    PyObject *errors = PyList_New(0);
    for (; n_errors > 0; n_errors--) {
	long error_code = *((long *)(ptr + index));
	index += sizeof(long);
	long error_line = *((long *)(ptr + index));
	index += sizeof(long);
	const char *error_msg = ptr + index;
	index += strlen(error_msg) + 1;
	const char *error_file = ptr + index;
	index += strlen(error_file) + 1;
	const char *error_func = ptr + index;
	index += strlen(error_func) + 1;
	PyList_Append(errors, Py_BuildValue("issis", error_code, error_msg, 
					    error_file, error_line, error_func));
    }

    PyObject *frames = PyList_New(0);
    while (index < ((long *)ptr)[0]) {
	const char *tag = ptr + index;
	index += strlen(tag) + 1;
	const char *file = ptr + index;
	index += strlen(file) + 1;
	PyList_Append(frames, Py_BuildValue("ss", tag, file));
    }

    return Py_BuildValue("OOO", frames, errors, stats);
}

static void *sbuffer_append_string(void *buf, const char *str) {
    buf = realloc(buf, ((long *)buf)[0] + strlen(str) + 1);
    strcpy(buf + *((long *)buf), str);
    *((long *)buf) += strlen(str) + 1;
    return buf;
}

static void *sbuffer_append_bytes(void *buf, const void *src, size_t nbytes) {
    buf = realloc(buf, ((long *)buf)[0] + nbytes);
    memcpy(buf + *((long *)buf), src, nbytes);
    *((long *)buf) += nbytes;
    return buf;
}

static void *sbuffer_append_long(void *buf, long val) {
    buf = realloc(buf, *((long *)buf) + sizeof(long));
    *((long *)(buf + ((long *)buf)[0])) = val;
    *((long *)buf) += sizeof(long);
    return buf;
}

static void *serialized_error_ptr = NULL;
static cpl_library_t *serialized_cpl = NULL;

static void 
exec_serialize_one_error(unsigned self, unsigned first, unsigned last) {
    if (serialized_error_ptr == NULL) {
	serialized_error_ptr = malloc(sizeof(long));
	((long *)serialized_error_ptr)[0] = sizeof(long);
	serialized_error_ptr = sbuffer_append_long(serialized_error_ptr, 0);
    }
    if (serialized_cpl->error_get_code() == CPL_ERROR_NONE) {
	return;
    }
    ((long *)serialized_error_ptr)[1]++; // number of errors

    serialized_error_ptr = sbuffer_append_long(serialized_error_ptr, 
					       serialized_cpl->error_get_code());
    serialized_error_ptr = sbuffer_append_long(serialized_error_ptr, 
					       serialized_cpl->error_get_line());
    serialized_error_ptr = sbuffer_append_string(serialized_error_ptr, 
						 serialized_cpl->error_get_message());
    serialized_error_ptr = sbuffer_append_string(serialized_error_ptr, 
						 serialized_cpl->error_get_file());
    serialized_error_ptr = sbuffer_append_string(serialized_error_ptr, 
						 serialized_cpl->error_get_function());
}

static void *
exec_serialize_retval(CPL_recipe *self, cpl_frameset *frames, 
		      cpl_errorstate prestate, int retval, 
		      const struct tms *tms_clock) {
    int n_frames = self->cpl->frameset_get_size(frames);
    int i_frame;
    void *ptr = malloc(sizeof(long));
    ((long *)ptr)[0] = sizeof(long);
    ptr = sbuffer_append_long(ptr, retval);
    ptr = sbuffer_append_long(ptr, 1000000L * 
			      (tms_clock->tms_utime + tms_clock->tms_cutime) 
			      / sysconf(_SC_CLK_TCK));
    ptr = sbuffer_append_long(ptr, 1000000L * 
			      (tms_clock->tms_stime + tms_clock->tms_cstime)
			      / sysconf(_SC_CLK_TCK));
    ptr = sbuffer_append_long(ptr, self->cpl->memory_is_empty());

    serialized_cpl = self->cpl;
    self->cpl->errorstate_dump(prestate, CPL_FALSE, exec_serialize_one_error);
    ptr = sbuffer_append_bytes(ptr, serialized_error_ptr + sizeof(long),
			       ((long *)serialized_error_ptr)[0] - sizeof(long));
    free(serialized_error_ptr);
    serialized_error_ptr = NULL;
    serialized_cpl = NULL;

    for (i_frame = 0; i_frame < n_frames; i_frame++) {
	cpl_frame *f = self->cpl->frameset_get_position(frames, i_frame);
	if (self->cpl->frame_get_group(f) != CPL_FRAME_GROUP_PRODUCT) {
	    continue;
	}
	ptr = sbuffer_append_string(ptr, self->cpl->frame_get_tag(f));
	ptr = sbuffer_append_string(ptr, self->cpl->frame_get_filename(f));
    }
    return ptr;
}
static int do_backtrace(void) {
  char cmd[300];
  snprintf(cmd, sizeof(cmd), 
	   "cat >> gdb_commands << EOF\n"
	   "set height 0\nset width 0\nbt full\ninfo sources\ninfo files\n"
	   "EOF");
  int retval = system(cmd);
  snprintf(cmd, sizeof(cmd), 
	   "gdb -batch -x gdb_commands --pid %i --readnow  >> recipe.backtrace-unprocessed 2> /dev/null", 
	   (int)getpid());
  retval |= system(cmd);
  unlink("gdb_commands");
  return retval;
  
}

#ifdef HAVE_MCHECK
static void mcheck_handler(enum mcheck_status status) {
  char cmd[100];
  snprintf(cmd, sizeof(cmd), 
	   "echo Memory corruption > recipe.backtrace-unprocessed");
  int retval = system(cmd);
  if (retval == 0) {
      do_backtrace();
  }
  abort();
}
#endif

static int segv_handler(int sig) {
  char cmd[100];
  snprintf(cmd, sizeof(cmd), 
	   "echo Received signal: %i > recipe.backtrace-unprocessed", sig);
  int retval = system(cmd);
  do_backtrace();

  signal(sig, SIG_DFL);
  return retval;
}

static void setup_tracing(CPL_recipe *self, int memory_trace) {

#ifdef HAVE_PRCTL
#ifdef PR_SET_PTRACER
/* Sets the top of the process tree that is allowed to use PTRACE on the
   calling process */
    prctl(PR_SET_PTRACER, getpid(), 0, 0, 0);
#endif
#ifdef PR_SET_NAME
/*  Set  the  process  name  for  the  calling  process */
    prctl(PR_SET_NAME, self->cpl->plugin_get_name(self->plugin), 0, 0, 0);
#endif
#endif
#ifdef HAVE_MCHECK
    mcheck(mcheck_handler);
#endif
#ifdef HAVE_MALLOPT
    mallopt(M_CHECK_ACTION, 0);
#endif
#ifdef HAVE_MTRACE
    if (memory_trace) {
	setenv("MALLOC_TRACE", "recipe.mtrace", 1);
	mtrace();
    }
#endif

    typedef void (*sighandler_t)(int);

    signal(SIGSEGV, (sighandler_t) segv_handler);
    signal(SIGINT, (sighandler_t) segv_handler);
    signal(SIGHUP, (sighandler_t) segv_handler);
    signal(SIGFPE, (sighandler_t) segv_handler);
    signal(SIGQUIT, (sighandler_t) segv_handler);
    signal(SIGBUS, (sighandler_t) segv_handler);
    signal(SIGTERM, (sighandler_t) segv_handler);
    signal(SIGABRT, (sighandler_t) segv_handler);
    signal(SIGTERM, (sighandler_t) segv_handler);
}

#define CPL_recipe_exec_doc                                             \
    "Execute with parameters and frames.\n\n"                           \
    "The parameters shall contain an iterable of (name, value) pairs\n" \
    "where the values have the correct type for the parameter.\n"       \
    "The frames shall contain an iterable of (name, tag) pairs."

static PyObject *
CPL_recipe_exec(CPL_recipe *self, PyObject *args) {
    PyObject *parlist;
    PyObject *soflist;
    PyObject *runenv;
    const char *dirname;
    const char *logfile;
    int loglevel;
    int memory_dump;
    int memory_trace;
    if (!PyArg_ParseTuple(args, "sOOOsiii", &dirname, &parlist, &soflist,
			  &runenv, &logfile, &loglevel,
			  &memory_dump, &memory_trace))
        return NULL;
    if (!PySequence_Check(parlist)) {
	PyErr_SetString(PyExc_TypeError, "Second parameter not a list");
	return NULL;
    }
    if (!PySequence_Check(soflist)) {
	PyErr_SetString(PyExc_TypeError, "Third parameter not a list");
	return NULL;
    }
    if (!PySequence_Check(runenv)) {
	PyErr_SetString(PyExc_TypeError, "Fourth parameter not a list");
	return NULL;
    }

    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    self->cpl->error_reset();
    cpl_recipe *recipe = (cpl_recipe *)self->plugin;
    self->cpl->frameset_delete(recipe->frames);
    recipe->frames = get_frames(self, soflist);
    clear_parameters(self, recipe->parameters);
    set_parameters(self, recipe->parameters, parlist);
    if (self->cpl->error_get_code() != CPL_ERROR_NONE) {
	PyErr_SetString(PyExc_IOError, "CPL error on inititalization");
	return NULL;	
    }
    int fd[2];
    if (pipe(fd) == -1) {
	PyErr_SetString(PyExc_IOError, "Cannot pipe()");
	return NULL;
    }
    pid_t childpid = fork();
    if (childpid == -1) {
	PyErr_SetString(PyExc_IOError, "Cannot fork()");
	return NULL;
    }
    
    if (childpid == 0) {
	close(fd[0]);
	int retval;
	struct tms clock_end;
	set_environment(runenv);
	self->cpl->msg_set_log_name(logfile);
	self->cpl->msg_set_log_level(loglevel);
	self->cpl->msg_set_level(CPL_MSG_OFF);
	cpl_errorstate prestate = self->cpl->errorstate_get();
	if (chdir(dirname) == 0) {
	    struct tms clock_start;
	    times(&clock_start);
	    setup_tracing(self, memory_trace);
	    retval = self->cpl->plugin_get_exec(self->plugin)(self->plugin);
	    int reto = self->cpl->dfs_update_product_header(recipe->frames);
	    if (reto != CPL_ERROR_NONE) {
		self->cpl->msg_error (__func__, "could not update the product header");
	    }
	    times(&clock_end);
	    clock_end.tms_utime -= clock_start.tms_utime;
	    clock_end.tms_stime -= clock_start.tms_stime;
	    clock_end.tms_cutime -= clock_start.tms_cutime;
	    clock_end.tms_cstime -= clock_start.tms_cstime;
	    self->cpl->msg_stop_log();
	} else {
	    retval = CPL_ERROR_FILE_NOT_CREATED;
	    self->cpl->error_set_message_macro(__func__, retval, __FILE__, __LINE__, " ");
	}
	void *ptr = exec_serialize_retval(self, recipe->frames, prestate,
					  retval, &clock_end);
	long n_bytes = write(fd[1], ptr, ((long *)ptr)[0]);
	close(fd[1]);
	retval = (n_bytes != ((long *)ptr)[0]);
	free(ptr);
	self->cpl->frameset_delete(recipe->frames);
	self->cpl->parameterlist_delete(recipe->parameters);
	recipe->parameters = NULL;
	recipe->frames = NULL;
	self->cpl->plugin_get_deinit(self->plugin)(self->plugin);
	self->cpl->pluginlist_delete(self->pluginlist);
	Py_TYPE(self)->tp_free((PyObject*)self);
	if ((memory_dump > 1)
	    || ((memory_dump > 0) && (!self->cpl->memory_is_empty()))) {
	  self->cpl->memory_dump();
	}
	self->cpl->end();
#ifdef HAVE_MTRACE
	muntrace();
#endif
	_exit(retval);
    }
    
    close(fd[1]);
    long nbytes;
    void *ptr = malloc(2 * sizeof(long));
Py_BEGIN_ALLOW_THREADS
    nbytes = read(fd[0], ptr, 2 * sizeof(long));
    if (nbytes == 2 * sizeof(long)) {
	ptr = realloc(ptr, ((long *)ptr)[0]);
	nbytes += read(fd[0], ptr + 2 * sizeof(long), 
		       ((long *)ptr)[0] - 2 * sizeof(long));
    } else { // broken pipe while reading first two bytes
	((long *)ptr)[0] = 2 * sizeof(long); 
    }
    close(fd[0]);
    waitpid(childpid, NULL, 0);
Py_END_ALLOW_THREADS
    if (nbytes != ((long *)ptr)[0]) {
	PyErr_SetString(PyExc_IOError, "Recipe crashed");
	return NULL;
    }
    PyObject *retval = exec_build_retval(ptr);
    free(ptr);
    return retval;
}

static PyMethodDef CPL_recipe_methods[] = {
    {"params",  (PyCFunction)CPL_recipe_get_params, METH_NOARGS,
     CPL_recipe_get_params_doc},
    {"author",  (PyCFunction)CPL_recipe_get_author, METH_NOARGS,
     CPL_recipe_get_author_doc},
    {"version",  (PyCFunction)CPL_recipe_get_version, METH_NOARGS,
     CPL_recipe_get_version_doc},
    {"description",  (PyCFunction)CPL_recipe_get_description, METH_NOARGS,
     CPL_recipe_get_description_doc},
    {"copyright",  (PyCFunction)CPL_recipe_get_copyright, METH_NOARGS,
     CPL_recipe_get_copyright_doc},
    {"frameConfig",  (PyCFunction)CPL_recipe_get_frameconfig, METH_NOARGS,
     CPL_recipe_get_frameconfig_doc},
    {"run",  (PyCFunction)CPL_recipe_exec, METH_VARARGS,
     CPL_recipe_exec_doc},
    {"cpl_is_supported", (PyCFunction)CPL_is_supported, METH_NOARGS,
     CPL_is_supported_doc},
    {"cpl_version", (PyCFunction)CPL_version, METH_NOARGS, CPL_version_doc},
    {"cpl_description", (PyCFunction)CPL_description, METH_NOARGS, CPL_version_doc},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyTypeObject CPL_recipeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "CPL_recipe.recipe",       /*tp_name*/
    sizeof(CPL_recipe),        /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)CPL_recipe_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    CPL_recipe_doc,            /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    CPL_recipe_methods,        /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CPL_recipe_init, /* tp_init */
    0,                         /* tp_alloc */
    CPL_recipe_new,            /* tp_new */
};


#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_CPL_recipe(void) {
    static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "CPL_recipe",        /* m_name */
        NULL,                /* m_doc */
        -1,                  /* m_size */
        CPL_methods,         /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };

    CPL_recipeType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CPL_recipeType) < 0) {
        return NULL;
    }

    PyObject *m = PyModule_Create(&moduledef);
    Py_INCREF(&CPL_recipeType);
    PyModule_AddObject(m, "recipe", (PyObject *)&CPL_recipeType);
    return m;
}
#else
PyMODINIT_FUNC
initCPL_recipe(void) {
    CPL_recipeType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CPL_recipeType) < 0) {
	return;
    }

    PyObject *m = Py_InitModule3("CPL_recipe", CPL_methods, NULL);
    Py_INCREF(&CPL_recipeType);
    PyModule_AddObject(m, "recipe", (PyObject *)&CPL_recipeType);
}
#endif
