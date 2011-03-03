#include <Python.h>
#include <unistd.h>
#include <dlfcn.h>
#include <sys/wait.h>
#include <sys/times.h>
#include <sys/prctl.h>
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <cpl.h>

#define CPL_version_doc \
    "Get the CPL version string."

static PyObject *
CPL_version(PyObject *self) {
    return Py_BuildValue("s", cpl_version_get_version());
}

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

    dlerror();
    int (*cpl_plugin_get_info)(cpl_pluginlist *) = dlsym(handle,
							 "cpl_plugin_get_info");
    char *error = dlerror();
    if (error != NULL)  {
	Py_INCREF(Py_None);
	return Py_None;
    }
    PyObject *res = PyList_New(0);
    Py_INCREF(res);
    cpl_pluginlist *list = cpl_pluginlist_new();
    (*cpl_plugin_get_info)(list);
    cpl_plugin *plugin;
    for (plugin = cpl_pluginlist_get_first(list);
	 plugin != NULL;
	 plugin = cpl_pluginlist_get_next(list)) {
	cpl_error_reset();
	cpl_plugin_get_init(plugin)(plugin);
	PyList_Append(res, Py_BuildValue("sis", 
					 cpl_plugin_get_name(plugin),
					 cpl_plugin_get_version(plugin),
					 cpl_plugin_get_version_string(plugin)));
	cpl_plugin_get_deinit(plugin)(plugin);
    }
    cpl_pluginlist_delete(list);
    cpl_error_reset();
    dlclose(handle);
    return res;
}

#define CPL_set_msg_level_doc \
    "Set verbosity level of output to terminal."

static PyObject *
CPL_set_msg_level(PyObject *self, PyObject *args) {
    int level;

    if (!PyArg_ParseTuple(args, "i", &level))
        return NULL;
    cpl_msg_set_level(level);

    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_get_msg_level_doc \
    "Get current terminal verbosity level."

static PyObject *
CPL_get_msg_level(PyObject *self) {
    return Py_BuildValue("i", cpl_msg_get_level());
}

#define CPL_set_msg_time_doc \
    "Enable or disable the time tag in output messages."

static PyObject *
CPL_set_msg_time(PyObject *self, PyObject *args) {
    PyObject *enable;
    if (!PyArg_ParseTuple(args, "O", &enable))
        return NULL;

    if (PyObject_IsTrue(enable)) {
	cpl_msg_set_time_on();
    } else {
	cpl_msg_set_time_off();
    }

    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_set_log_level_doc \
    "Set verbosity level of output to logfile."

static PyObject *
CPL_set_log_level(PyObject *self, PyObject *args) {
    int level;

    if (!PyArg_ParseTuple(args, "i", &level))
        return NULL;
    cpl_msg_set_log_level(level);

    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_get_log_level_doc \
    "Get current logfile verbosity level."

static PyObject *
CPL_get_log_level(PyObject *self) {
    return Py_BuildValue("i", cpl_msg_get_log_level());
}

#define CPL_set_log_file_doc \
    "Set the log file name."

static PyObject *
CPL_set_log_file(PyObject *self, PyObject *args) {
    const char *name;

    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    cpl_error_code r = cpl_msg_set_log_name(name);
    if (r != CPL_ERROR_NONE) {
	PyErr_SetString(PyExc_IOError, cpl_error_get_message());
	return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_get_log_file_doc \
    "Get the log file name."

static PyObject *
CPL_get_log_file(PyObject *self) {
    return Py_BuildValue("s", cpl_msg_get_log_name());
}

#define CPL_set_log_domain_doc \
    "Set the log domain name."

static PyObject *
CPL_set_log_domain(PyObject *self, PyObject *args) {
    const char *name;

    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    cpl_msg_set_domain(name);
    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_get_log_domain_doc \
    "Get the log domain name."

static PyObject *
CPL_get_log_domain(PyObject *self) {
    return Py_BuildValue("s", cpl_msg_get_domain());
}

#define CPL_log_doc \
    "Write a log message."

static PyObject *
CPL_log(PyObject *self, PyObject *args) {
    int level;
    const char *msg;
    const char *caller;
    if (!PyArg_ParseTuple(args, "iss", &level, &caller, &msg))
        return NULL;
    if (level < 0) level = 0;
    typedef void (*msg_func_t)(const char *, const char *,...);
    msg_func_t msg_func[]= {
	cpl_msg_debug,
	cpl_msg_info,
	cpl_msg_warning,
	cpl_msg_error
    };
    if (level <=3) {
	msg_func[level](caller, "%s", msg);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_log_indent_more_doc \
    "Increase the message indentation by one indentation step."

static PyObject *
CPL_log_indent_more(PyObject *self) {
    cpl_msg_indent_more();
    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_log_indent_less_doc \
    "Decrease the message indentation by one indentation step."

static PyObject *
CPL_log_indent_less(PyObject *self) {
    cpl_msg_indent_less();
    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_memory_dump_doc \
    "Display the memory status."

static PyObject *
CPL_memory_dump(PyObject *self) {
    cpl_memory_dump();
    Py_INCREF(Py_None);
    return Py_None;
}

#define CPL_memory_is_empty_doc \
    "Tell if there is some memory allocated."

static PyObject *
CPL_memory_is_empty(PyObject *self) {
    return Py_BuildValue("i", cpl_memory_is_empty());
}

static PyMethodDef CPL_methods[] = {
    {"version", (PyCFunction)CPL_version, METH_NOARGS, CPL_version_doc},
    {"list", CPL_list, METH_VARARGS, CPL_list_doc},
    {"set_msg_level", CPL_set_msg_level, METH_VARARGS, CPL_set_msg_level_doc},
    {"get_msg_level", (PyCFunction)CPL_get_msg_level, METH_NOARGS, 
     CPL_get_msg_level_doc},
    {"set_msg_time", CPL_set_msg_time, METH_VARARGS, CPL_set_msg_time_doc },
    {"set_log_level", CPL_set_log_level, METH_VARARGS, CPL_set_log_level_doc},
    {"get_log_level", (PyCFunction)CPL_get_log_level, METH_NOARGS, 
     CPL_get_log_level_doc},
    {"set_log_file", CPL_set_log_file, METH_VARARGS, CPL_set_log_file_doc},
    {"get_log_file", (PyCFunction)CPL_get_log_file, METH_NOARGS, 
     CPL_get_log_file_doc },
    {"set_log_domain", CPL_set_log_domain, METH_VARARGS, 
     CPL_set_log_domain_doc},
    {"get_log_domain", (PyCFunction)CPL_get_log_domain, METH_NOARGS, 
     CPL_get_log_domain_doc },
    {"log", CPL_log, METH_VARARGS, CPL_log_doc}, 
    {"log_indent_more", (PyCFunction)CPL_log_indent_more, METH_NOARGS, 
     CPL_log_indent_more_doc},
    {"log_indent_less", (PyCFunction)CPL_log_indent_less, METH_NOARGS, 
     CPL_log_indent_less_doc},
    {"memory_dump", (PyCFunction)CPL_memory_dump, METH_NOARGS, 
     CPL_memory_dump_doc},
    {"memory_is_empty", (PyCFunction)CPL_memory_is_empty, METH_NOARGS, 
     CPL_memory_is_empty_doc},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

typedef struct {
    PyObject_HEAD
    cpl_plugin *plugin;
    cpl_pluginlist *pluginlist;
    void *handle;
    cpl_recipeconfig *recipeconfig;
} CPL_recipe;

static void
CPL_recipe_dealloc(CPL_recipe* self) {
    if (self->plugin != NULL) {
	cpl_plugin_get_deinit(self->plugin)(self->plugin);
    }
    if (self->pluginlist != NULL) {
	cpl_pluginlist_delete(self->pluginlist);
    }
    if (self->handle != NULL) {
	dlclose(self->handle);
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CPL_recipe_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    CPL_recipe *self = (CPL_recipe *)type->tp_alloc(type, 0);
    if (self != NULL) {
	self->plugin = NULL;
	self->pluginlist = NULL;
	self->handle = NULL;
	self->recipeconfig = NULL;
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
    cpl_error_reset();
    self->pluginlist = cpl_pluginlist_new();
    (*cpl_plugin_get_info)(self->pluginlist);
    self->plugin = cpl_pluginlist_find(self->pluginlist, recipe);
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "cannot find recipe in shared library");
	return -1;
    } else {
	cpl_plugin_get_init(self->plugin)(self->plugin);
    }
    
    cpl_recipeconfig *(*get_recipeconfig)(cpl_recipe *) 
	= dlsym(self->handle, "muse_processing_get_recipeconfig");
    if (dlerror() == NULL && get_recipeconfig != NULL) {
	self->recipeconfig = get_recipeconfig((cpl_recipe *)self->plugin);
    } else {
	self->recipeconfig = NULL;
    }
    return 0;
}

static PyObject *
getParameter(cpl_parameter *param) {
    cpl_type type = cpl_parameter_get_type(param);
    cpl_parameter_class class = cpl_parameter_get_class(param);
    const char *name = cpl_parameter_get_alias(param, 
					       CPL_PARAMETER_MODE_CLI);
    const char *fullname = cpl_parameter_get_name(param);
    const char *context = cpl_parameter_get_context(param);
    const char *help = cpl_parameter_get_help(param);
    PyObject *range = Py_None;
    if (class == CPL_PARAMETER_CLASS_RANGE) {
	switch (type) {
	    case CPL_TYPE_INT:
		range = Py_BuildValue("ii",
				      cpl_parameter_get_range_min_int(param),
				      cpl_parameter_get_range_max_int(param));
		break;
	    case CPL_TYPE_DOUBLE:
		range = Py_BuildValue("dd",
				      cpl_parameter_get_range_min_double(param),
				      cpl_parameter_get_range_max_double(param));
		break;
	    default:
		break;
	}
    }
    Py_INCREF(range);
    PyObject *sequence = Py_None;
    if (class == CPL_PARAMETER_CLASS_ENUM) {
	sequence = PyList_New(0);
	int n_enum = cpl_parameter_get_enum_size(param);
	int i;
	for (i = 0; i < n_enum; i++) {
	    switch (type) {
		case CPL_TYPE_INT:
		    PyList_Append(
			sequence, 
			Py_BuildValue("i",
				      cpl_parameter_get_enum_int(param, i)));
		    break;
		case CPL_TYPE_DOUBLE:
		    PyList_Append(
			sequence, 
			Py_BuildValue("d",
				      cpl_parameter_get_enum_double(param, i)));
		    break;
		case CPL_TYPE_STRING:
		    PyList_Append(
			sequence, 
			Py_BuildValue("s",
				      cpl_parameter_get_enum_string(param, i)));
		    break;
		default:
		    break;
	    }
	}
    }
    Py_INCREF(sequence);
    PyObject *deflt = Py_None;
    PyObject *ptype = Py_None;
    switch (type) {
	case CPL_TYPE_BOOL:
	    ptype = (PyObject *)&PyBool_Type;
	    deflt = (cpl_parameter_get_default_bool(param))?Py_True:Py_False;
	    break;
	case CPL_TYPE_INT:
	    ptype = (PyObject *)&PyInt_Type;
	    deflt = Py_BuildValue("i", cpl_parameter_get_default_int(param));
	    break;
	case CPL_TYPE_DOUBLE:
	    ptype = (PyObject *)&PyFloat_Type;
	    deflt = Py_BuildValue("d", cpl_parameter_get_default_double(param));
	    break;
	case CPL_TYPE_STRING:
	    ptype = (PyObject *)&PyString_Type;
	    deflt = Py_BuildValue("s", cpl_parameter_get_default_string(param));
	    break;
	default:
	    break;
    }
    Py_INCREF(deflt);
    Py_INCREF(ptype);

    PyObject *par = Py_BuildValue("ssssNNNN", 
				  name, context, fullname, help,
				  range, sequence, deflt, ptype);
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
    " - default value"

static PyObject *
CPL_recipe_get_params(CPL_recipe *self) {
    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    cpl_parameterlist *pars = ((cpl_recipe *)self->plugin)->parameters;
    PyObject *res = PyList_New(0);
    if (pars && cpl_parameterlist_get_size(pars)) {
	cpl_parameter *param;
	for (param = cpl_parameterlist_get_first(pars);
	     param != NULL;  
	     param = cpl_parameterlist_get_next(pars)) {
	    PyList_Append(res, getParameter(param));
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
			 cpl_plugin_get_author(self->plugin),
			 cpl_plugin_get_email(self->plugin));
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
			 cpl_plugin_get_synopsis(self->plugin),
			 cpl_plugin_get_description(self->plugin));
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
			 cpl_plugin_get_version(self->plugin),
			 cpl_plugin_get_version_string(self->plugin));
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
			 cpl_plugin_get_copyright(self->plugin));
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
    char **tags = cpl_recipeconfig_get_tags(self->recipeconfig);
    int i_tag;
    for (i_tag = 0; tags[i_tag] != NULL; i_tag++) {
	int min = cpl_recipeconfig_get_min_count(self->recipeconfig,
						 tags[i_tag], tags[i_tag]);
	int max = cpl_recipeconfig_get_max_count(self->recipeconfig,
						 tags[i_tag], tags[i_tag]);
	PyObject *raw = Py_BuildValue("sii", tags[i_tag], min, max);
	PyObject *calib = PyList_New(0);

	char **inputs = cpl_recipeconfig_get_inputs(self->recipeconfig,
						    tags[i_tag]);
	int i_input;
	for (i_input = 0; inputs[i_input] != NULL; i_input++) {
	    int min = cpl_recipeconfig_get_min_count(self->recipeconfig,
						     tags[i_tag], 
						     inputs[i_input]);
	    int max = cpl_recipeconfig_get_max_count(self->recipeconfig,
						     tags[i_tag], 
						     inputs[i_input]);
	    PyList_Append(calib, Py_BuildValue("sii", inputs[i_input], 
					       min, max));
	    cpl_free(inputs[i_input]);
	}
	cpl_free(inputs);

	PyObject *output = PyList_New(0);
	char **outputs = cpl_recipeconfig_get_outputs(self->recipeconfig,
						      tags[i_tag]);
	int i_output;
	for (i_output = 0; outputs[i_output] != NULL; i_output++) {
	    PyList_Append(output, Py_BuildValue("s", outputs[i_output]));
	    cpl_free(outputs[i_output]);
	}
	cpl_free(outputs);
	
	PyList_Append(res, Py_BuildValue("OOO", raw, calib, output));
	
	cpl_free(tags[i_tag]);
    }
    cpl_free(tags);
    return res;
}

static cpl_frameset *
get_frames(PyObject *framelist) {
    cpl_frameset *frames = cpl_frameset_new();
    PyObject *iter = PyObject_GetIter(framelist);
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
	const char *tag;
	const char* file;
	PyArg_ParseTuple(item, "ss", &tag, &file);
	cpl_frame *frame = cpl_frame_new();
	cpl_frame_set_filename(frame, file);
	cpl_frame_set_tag(frame, tag);
	cpl_frameset_insert(frames, frame);
	Py_DECREF(item);
    }
    Py_DECREF(iter);
    return frames;
}

static void 
clear_parameters(cpl_parameterlist *parameters) {
    cpl_parameter *par = cpl_parameterlist_get_first(parameters);
    while (par != NULL) {
	cpl_type type = cpl_parameter_get_type(par);
	switch(type) {
	    case CPL_TYPE_STRING:
		cpl_parameter_set_string(par, 
					 cpl_parameter_get_default_string(par));
		break;
	    case CPL_TYPE_INT:
		cpl_parameter_set_int(par, 
				      cpl_parameter_get_default_int(par));
		break;
	    case CPL_TYPE_DOUBLE:
		cpl_parameter_set_double(par, 
					 cpl_parameter_get_default_double(par));
		break;
	    case CPL_TYPE_BOOL:
		cpl_parameter_set_bool(par, 
				       cpl_parameter_get_default_bool(par));
		break;
	    default:
		break;
	}
	
	par = cpl_parameterlist_get_next(parameters);
    }
    
}

static void
set_parameters(cpl_parameterlist *parameters, PyObject *parlist) {
    PyObject *iter = PyObject_GetIter(parlist);
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
	const char *name;
	PyObject *value;
	PyArg_ParseTuple(item, "sO", &name, &value);
	cpl_parameter *par = cpl_parameterlist_find(parameters, name);
	if (par == NULL) {
	    continue;
	}
	cpl_type type = cpl_parameter_get_type(par);
	switch(type) {
	    case CPL_TYPE_STRING:
		if (PyString_Check(value)) {
		    cpl_parameter_set_string(par, PyString_AsString(value));
		}
		break;
	    case CPL_TYPE_INT:
		if (PyInt_Check(value)) {
		    cpl_parameter_set_int(par, PyInt_AsLong(value));
		}
		break;
	    case CPL_TYPE_DOUBLE:
		if (PyFloat_Check(value)) {
		    cpl_parameter_set_double(par, PyFloat_AsDouble(value));
		}
		break;
	    case CPL_TYPE_BOOL:
		cpl_parameter_set_bool(par, PyObject_IsTrue(value));
		break;
	    default:
		break;
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
    buf = cpl_realloc(buf, ((long *)buf)[0] + strlen(str) + 1);
    strcpy(buf + *((long *)buf), str);
    *((long *)buf) += strlen(str) + 1;
    return buf;
}

static void *sbuffer_append_bytes(void *buf, const void *src, size_t nbytes) {
    buf = cpl_realloc(buf, ((long *)buf)[0] + nbytes);
    memcpy(buf + *((long *)buf), src, nbytes);
    *((long *)buf) += nbytes;
    return buf;
}

static void *sbuffer_append_long(void *buf, long val) {
    buf = cpl_realloc(buf, *((long *)buf) + sizeof(long));
    *((long *)(buf + ((long *)buf)[0])) = val;
    *((long *)buf) += sizeof(long);
    return buf;
}

static void *serialized_error_ptr = NULL;

static void 
exec_serialize_one_error(unsigned self, unsigned first, unsigned last) {
    if (serialized_error_ptr == NULL) {
	serialized_error_ptr = cpl_malloc(sizeof(long));
	((long *)serialized_error_ptr)[0] = sizeof(long);
	serialized_error_ptr = sbuffer_append_long(serialized_error_ptr, 0);
    }
    if (cpl_error_get_code() == CPL_ERROR_NONE) {
	return;
    }
    ((long *)serialized_error_ptr)[1]++; // number of errors

    serialized_error_ptr = sbuffer_append_long(serialized_error_ptr, 
					       cpl_error_get_code());
    serialized_error_ptr = sbuffer_append_long(serialized_error_ptr, 
					       cpl_error_get_line());
    serialized_error_ptr = sbuffer_append_string(serialized_error_ptr, 
						 cpl_error_get_message());
    serialized_error_ptr = sbuffer_append_string(serialized_error_ptr, 
						 cpl_error_get_file());
    serialized_error_ptr = sbuffer_append_string(serialized_error_ptr, 
						 cpl_error_get_function());
}

static void *
exec_serialize_retval(cpl_frameset *frames, cpl_errorstate prestate, int retval, 
		      const struct tms *tms_clock) {
    int n_frames = cpl_frameset_get_size(frames);
    int i_frame;
    void *ptr = cpl_malloc(sizeof(long));
    ((long *)ptr)[0] = sizeof(long);
    ptr = sbuffer_append_long(ptr, retval);
    ptr = sbuffer_append_long(ptr, 1000000L * 
			      (tms_clock->tms_utime + tms_clock->tms_cutime) 
			      / sysconf(_SC_CLK_TCK));
    ptr = sbuffer_append_long(ptr, 1000000L * 
			      (tms_clock->tms_stime + tms_clock->tms_cstime)
			      / sysconf(_SC_CLK_TCK));
    ptr = sbuffer_append_long(ptr, cpl_memory_is_empty());

    cpl_errorstate_dump(prestate, CPL_FALSE, exec_serialize_one_error);
    ptr = sbuffer_append_bytes(ptr, serialized_error_ptr + sizeof(long),
			       ((long *)serialized_error_ptr)[0] - sizeof(long));
    cpl_free(serialized_error_ptr);
    serialized_error_ptr = NULL;

    for (i_frame = 0; i_frame < n_frames; i_frame++) {
	cpl_frame *f = cpl_frameset_get_frame(frames, i_frame);
	if (cpl_frame_get_group(f) != CPL_FRAME_GROUP_PRODUCT) {
	    continue;
	}
	ptr = sbuffer_append_string(ptr, cpl_frame_get_tag(f));
	ptr = sbuffer_append_string(ptr, cpl_frame_get_filename(f));
    }
    return ptr;
}

static int segv_handler(int sig) {
    FILE *fp = fopen("gdb_commands", "w");
    const char *gdb_commands = "set height 0\nset width 0\nbt full\ninfo sources\n";
    fprintf(fp, "%s", gdb_commands);
    fclose(fp);
  
    char cmd[100];
    snprintf(cmd, sizeof(cmd), 
	     "gdb -batch -x gdb_commands --pid %i > recipe.backtrace 2> /dev/null", 
	     (int)getpid());
    system(cmd);
    unlink("gdb_commands");
    signal(SIGSEGV, SIG_DFL);
    return 0;
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
    const char *dirname;
    const char *logfile;
    int loglevel;
    if (!PyArg_ParseTuple(args, "sOOsi", &dirname, &parlist, &soflist,
			  &logfile, &loglevel))
        return NULL;
    if (!PySequence_Check(parlist)) {
	PyErr_SetString(PyExc_TypeError, "Second parameter not a list");
	return NULL;
    }
    if (!PySequence_Check(soflist)) {
	PyErr_SetString(PyExc_TypeError, "Third parameter not a list");
	return NULL;
    }

    if (self->plugin == NULL) {
	PyErr_SetString(PyExc_IOError, "NULL recipe");
	return NULL;
    }
    cpl_error_reset();
    cpl_recipe *recipe = (cpl_recipe *)self->plugin;
    cpl_frameset_delete(recipe->frames);
    recipe->frames = get_frames(soflist);
    clear_parameters(recipe->parameters);
    set_parameters(recipe->parameters, parlist);
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
	cpl_msg_set_log_name(logfile);
	cpl_msg_set_log_level(loglevel);
	cpl_errorstate prestate = cpl_errorstate_get();
	if (chdir(dirname) == 0) {
	    struct tms clock_start;
	    times(&clock_start);
#ifdef PR_SET_PTRACER
	    prctl(PR_SET_PTRACER, getpid(), 0, 0, 0);
#endif
	    signal(SIGSEGV, (sighandler_t) segv_handler);
	    signal(SIGBUS, (sighandler_t) segv_handler);
	    retval = cpl_plugin_get_exec(self->plugin)(self->plugin);
	    times(&clock_end);
	    clock_end.tms_utime -= clock_start.tms_utime;
	    clock_end.tms_stime -= clock_start.tms_stime;
	    clock_end.tms_cutime -= clock_start.tms_cutime;
	    clock_end.tms_cstime -= clock_start.tms_cstime;
	    cpl_msg_stop_log();
	} else {
	    retval = CPL_ERROR_FILE_NOT_CREATED;
	    cpl_error_set(__func__, retval);
	}
	void *ptr = exec_serialize_retval(recipe->frames, prestate,
					  retval, &clock_end);
	long n_bytes = write(fd[1], ptr, ((long *)ptr)[0]);
	close(fd[1]);
	exit(n_bytes != ((long *)ptr)[0]);
    }
    
    close(fd[1]);
    long nbytes;
    void *ptr = cpl_malloc(2 * sizeof(long));
Py_BEGIN_ALLOW_THREADS
    nbytes = read(fd[0], ptr, 2 * sizeof(long));
    if (nbytes == 2 * sizeof(long)) {
	ptr = cpl_realloc(ptr, ((long *)ptr)[0]);
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
    cpl_free(ptr);
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
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyTypeObject CPL_recipeType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
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

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
initCPL_recipe(void)
{
    cpl_init(CPL_INIT_DEFAULT);

    CPL_recipeType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CPL_recipeType) < 0)
        return;
    PyObject *m = Py_InitModule("CPL_recipe", CPL_methods);
    Py_INCREF(&CPL_recipeType);
    PyModule_AddObject(m, "recipe", (PyObject *)&CPL_recipeType);
}

