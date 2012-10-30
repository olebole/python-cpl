#include <stdlib.h>
#include <dlfcn.h>

#include "CPL_library.h"

#if CPL_VERSION_CODE < CPL_VERSION(6,0,0)
#error CPL version too old. Minimum required version is 6.0.0.
#endif
#if CPL_VERSION_CODE > CPL_VERSION(6,1,1)
#warning Newer CPL version: check API compability with 6.1.1 at http://upstream-tracker.org/versions/cpl.html
#endif

static cpl_library_t **libraries = NULL;

cpl_library_t *create_library(const char *fname) {
    void *handle = dlopen(fname, RTLD_LAZY);
    if (handle == NULL) {
	return NULL;
    }

    char *error = dlerror();
    typeof(cpl_init) *init = dlsym(handle, "cpl_init");
    error = dlerror();
    if (error != NULL) {
	dlclose(handle);
	return NULL;
    }

    if (libraries == NULL) {
	libraries = malloc(sizeof(cpl_library_t *));
	libraries[0] = NULL;
    }

    int i;
    for (i = 0; libraries[i] != NULL; i++) {
	if (init == libraries[i]->init) {
	    dlclose(handle);
	    return libraries[i];
	}
    }

    cpl_library_t *cpl = malloc(sizeof(cpl_library_t));
    cpl->init = init;

    cpl->get_description = dlsym(handle, "cpl_get_description");
    cpl->memory_dump = dlsym(handle, "cpl_memory_dump");
    cpl->memory_is_empty = dlsym(handle, "cpl_memory_is_empty");
    cpl->free = dlsym(handle, "cpl_free");

    cpl->plugin_get_author = dlsym(handle, "cpl_plugin_get_author");
    cpl->plugin_get_copyright = dlsym(handle, "cpl_plugin_get_copyright");
    cpl->plugin_get_deinit = dlsym(handle, "cpl_plugin_get_deinit");
    cpl->plugin_get_description = dlsym(handle, "cpl_plugin_get_description");
    cpl->plugin_get_email = dlsym(handle, "cpl_plugin_get_email");
    cpl->plugin_get_exec = dlsym(handle, "cpl_plugin_get_exec");
    cpl->plugin_get_init = dlsym(handle, "cpl_plugin_get_init");
    cpl->plugin_get_name = dlsym(handle, "cpl_plugin_get_name");
    cpl->plugin_get_synopsis = dlsym(handle, "cpl_plugin_get_synopsis");
    cpl->plugin_get_version = dlsym(handle, "cpl_plugin_get_version");
    cpl->plugin_get_version_string = dlsym(handle, "cpl_plugin_get_version_string");
    cpl->pluginlist_delete = dlsym(handle, "cpl_pluginlist_delete");
    cpl->pluginlist_find = dlsym(handle, "cpl_pluginlist_find");
    cpl->pluginlist_get_first = dlsym(handle, "cpl_pluginlist_get_first");
    cpl->pluginlist_get_next = dlsym(handle, "cpl_pluginlist_get_next");
    cpl->pluginlist_new = dlsym(handle, "cpl_pluginlist_new");

    cpl->dfs_update_product_header = dlsym(handle, "cpl_dfs_update_product_header");

    cpl->error_get_code = dlsym(handle, "cpl_error_get_code");
    cpl->error_get_file = dlsym(handle, "cpl_error_get_file");
    cpl->error_get_function = dlsym(handle, "cpl_error_get_function");
    cpl->error_get_line = dlsym(handle, "cpl_error_get_line");
    cpl->error_get_message = dlsym(handle, "cpl_error_get_message");
    cpl->error_reset = dlsym(handle, "cpl_error_reset");
    cpl->error_set_message_macro = dlsym(handle, "cpl_error_set_message_macro");
    cpl->errorstate_dump = dlsym(handle, "cpl_errorstate_dump");
    cpl->errorstate_get = dlsym(handle, "cpl_errorstate_get");

    cpl->frame_get_filename = dlsym(handle, "cpl_frame_get_filename");
    cpl->frame_get_group = dlsym(handle, "cpl_frame_get_group");
    cpl->frame_get_tag = dlsym(handle, "cpl_frame_get_tag");
    cpl->frame_new = dlsym(handle, "cpl_frame_new");
    cpl->frame_set_filename = dlsym(handle, "cpl_frame_set_filename");
    cpl->frame_set_tag = dlsym(handle, "cpl_frame_set_tag");
    cpl->frameset_delete = dlsym(handle, "cpl_frameset_delete");
    cpl->frameset_get_frame = dlsym(handle, "cpl_frameset_get_frame");
    cpl->frameset_get_size = dlsym(handle, "cpl_frameset_get_size");
    cpl->frameset_insert = dlsym(handle, "cpl_frameset_insert");
    cpl->frameset_new = dlsym(handle, "cpl_frameset_new");

    cpl->msg_error = dlsym(handle, "cpl_msg_error");
    cpl->msg_set_level = dlsym(handle, "cpl_msg_set_level");
    cpl->msg_set_log_level = dlsym(handle, "cpl_msg_set_log_level");
    cpl->msg_set_log_name = dlsym(handle, "cpl_msg_set_log_name");
    cpl->msg_stop_log = dlsym(handle, "cpl_msg_stop_log");

    cpl->parameter_get_alias = dlsym(handle, "cpl_parameter_get_alias");
    cpl->parameter_get_class = dlsym(handle, "cpl_parameter_get_class");
    cpl->parameter_get_context = dlsym(handle, "cpl_parameter_get_context");
    cpl->parameter_get_default_bool = dlsym(handle, "cpl_parameter_get_default_bool");
    cpl->parameter_get_default_double = dlsym(handle, "cpl_parameter_get_default_double");
    cpl->parameter_get_default_int = dlsym(handle, "cpl_parameter_get_default_int");
    cpl->parameter_get_default_string = dlsym(handle, "cpl_parameter_get_default_string");
    cpl->parameter_get_enum_double = dlsym(handle, "cpl_parameter_get_enum_double");
    cpl->parameter_get_enum_int = dlsym(handle, "cpl_parameter_get_enum_int");
    cpl->parameter_get_enum_size = dlsym(handle, "cpl_parameter_get_enum_size");
    cpl->parameter_get_enum_string = dlsym(handle, "cpl_parameter_get_enum_string");
    cpl->parameter_get_help = dlsym(handle, "cpl_parameter_get_help");
    cpl->parameter_get_name = dlsym(handle, "cpl_parameter_get_name");
    cpl->parameter_get_range_max_double = dlsym(handle, "cpl_parameter_get_range_max_double");
    cpl->parameter_get_range_max_int = dlsym(handle, "cpl_parameter_get_range_max_int");
    cpl->parameter_get_range_min_double = dlsym(handle, "cpl_parameter_get_range_min_double");
    cpl->parameter_get_range_min_int = dlsym(handle, "cpl_parameter_get_range_min_int");
    cpl->parameter_get_type = dlsym(handle, "cpl_parameter_get_type");
    cpl->parameter_set_bool = dlsym(handle, "cpl_parameter_set_bool");
    cpl->parameter_set_double = dlsym(handle, "cpl_parameter_set_double");
    cpl->parameter_set_int = dlsym(handle, "cpl_parameter_set_int");
    cpl->parameter_set_string = dlsym(handle, "cpl_parameter_set_string");
    cpl->parameterlist_find = dlsym(handle, "cpl_parameterlist_find");
    cpl->parameterlist_get_first = dlsym(handle, "cpl_parameterlist_get_first");
    cpl->parameterlist_get_next = dlsym(handle, "cpl_parameterlist_get_next");
    cpl->parameterlist_get_size = dlsym(handle, "cpl_parameterlist_get_size");

    cpl->recipeconfig_get_inputs = dlsym(handle, "cpl_recipeconfig_get_inputs");
    cpl->recipeconfig_get_max_count = dlsym(handle, "cpl_recipeconfig_get_max_count");
    cpl->recipeconfig_get_min_count = dlsym(handle, "cpl_recipeconfig_get_min_count");
    cpl->recipeconfig_get_outputs = dlsym(handle, "cpl_recipeconfig_get_outputs");
    cpl->recipeconfig_get_tags = dlsym(handle, "cpl_recipeconfig_get_tags");
    cpl->version_get_version = dlsym(handle, "cpl_version_get_version");

    error = dlerror();
    if (error != NULL) {
	dlclose(handle);
	free(cpl);
	return NULL;
    }
    cpl->get_recipeconfig = dlsym(handle, "muse_processing_get_recipeconfig");
    dlerror();

    cpl->init(CPL_INIT_DEFAULT);

    typeof(cpl_version_get_major) *get_major = dlsym(handle,
						     "cpl_version_get_major");
    typeof(cpl_version_get_minor) *get_minor = dlsym(handle,
						     "cpl_version_get_minor");
    typeof(cpl_version_get_micro) *get_micro = dlsym(handle,
						     "cpl_version_get_micro");
    cpl->TYPE_BOOL = CPL_TYPE_BOOL;
    cpl->TYPE_INT = CPL_TYPE_INT;
    cpl->TYPE_DOUBLE = CPL_TYPE_DOUBLE;
    cpl->TYPE_STRING = CPL_TYPE_STRING;

    unsigned long cpl_version = CPL_VERSION(get_major(), get_minor(),
					    get_micro());

    /* We dont have information about CPL before 4.0.0. For safety, we 
       will not handle them.
    */
    if (cpl_version < CPL_VERSION(4,0,0)) {
	dlclose(handle);
	free(cpl);
	return NULL;
    }

    /* Between 5.3.1 and 6.0, the cpl_type enum changed.
       http://upstream-tracker.org/compat_reports/cpl/5.3.1_to_6.0/abi_compat_report.html#Medium_Risk_Problems
       for these changes; the numbers were taken from there. According to
       upstream-tracker, this seems to be the only relevant API change between
       4.0.0 and 6.1.1.

       Also the cpl_size is newly introduced (former it was int), in

       cpl_frame *cpl_frameset_get_frame(cpl_frameset *self, cpl_size position);
       cpl_size cpl_frameset_get_size(const cpl_frameset *self);
       cpl_size cpl_parameterlist_get_size(const cpl_parameterlist *self);
       cpl_size cpl_recipeconfig_get_min_count(const cpl_recipeconfig* self,
                                            const char* tag, const char* input);
       cpl_size cpl_recipeconfig_get_max_count(const cpl_recipeconfig* self,
                                            const char* tag, const char* input);

       Currently, we just ignore this :-)

    */
    if (cpl_version < CPL_VERSION(6,0,0)) {
	cpl->TYPE_INT = 256;
	cpl->TYPE_DOUBLE = 8192;
    }

    libraries = realloc(libraries, sizeof(cpl_library_t *) * (i+2));
    libraries[i] = cpl;
    libraries[i+1] = NULL;
    return cpl;
}

