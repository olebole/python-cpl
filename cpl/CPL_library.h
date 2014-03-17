
#ifndef CPL_LIBRARY_H
#define CPL_LIBRARY_H

/* For the header, either the CPL one can be used, or the header that was
   extracted from the 6.3 release. For API safety, it is better to include
   the one provided with python-cpl. The other option is just for the adoption
   to a new CPL version.
   */
#ifdef USE_INSTALLED_CPL_HEADER
#include <cpl.h>
#else
#include "cpl_api.h"
#endif

#if CPL_VERSION_CODE < CPL_VERSION(6,3,0)
#error CPL version too old. Minimum required version is 6.3.0.
#endif
#if CPL_VERSION_CODE > CPL_VERSION(6,3,0)
#warning Newer CPL version: check API compability with 6.3.0 at http://upstream-tracker.org/versions/cpl.html
#endif

extern unsigned long supported_versions[];
#define UNKNOWN_VERSION 0
#define KNOWN_MAJOR 1
#define KNOWN_VERSION 2

typedef struct {
    unsigned long version;
    int is_supported;

    typeof(cpl_init) *init;
    typeof(cpl_end) *end;
    typeof(cpl_get_description) *get_description;
    typeof(cpl_memory_dump) *memory_dump;
    typeof(cpl_memory_is_empty) *memory_is_empty;
    typeof(cpl_free) *free;

    typeof(cpl_plugin_get_author) *plugin_get_author;
    typeof(cpl_plugin_get_copyright) *plugin_get_copyright;
    typeof(cpl_plugin_get_deinit) *plugin_get_deinit;
    typeof(cpl_plugin_get_description) *plugin_get_description;
    typeof(cpl_plugin_get_email) *plugin_get_email;
    typeof(cpl_plugin_get_exec) *plugin_get_exec;
    typeof(cpl_plugin_get_init) *plugin_get_init;
    typeof(cpl_plugin_get_name) *plugin_get_name;
    typeof(cpl_plugin_get_synopsis) *plugin_get_synopsis;
    typeof(cpl_plugin_get_version) *plugin_get_version;
    typeof(cpl_plugin_get_version_string) *plugin_get_version_string;
    typeof(cpl_pluginlist_delete) *pluginlist_delete;
    typeof(cpl_pluginlist_find) *pluginlist_find;
    typeof(cpl_pluginlist_get_first) *pluginlist_get_first;
    typeof(cpl_pluginlist_get_next) *pluginlist_get_next;
    typeof(cpl_pluginlist_new) *pluginlist_new;

    typeof(cpl_dfs_update_product_header) *dfs_update_product_header;

    typeof(cpl_error_get_code) *error_get_code;
    typeof(cpl_error_get_file) *error_get_file;
    typeof(cpl_error_get_function) *error_get_function;
    typeof(cpl_error_get_line) *error_get_line;
    typeof(cpl_error_get_message) *error_get_message;
    typeof(cpl_error_reset) *error_reset;
    typeof(cpl_error_set_message_macro) *error_set_message_macro;
    typeof(cpl_errorstate_dump) *errorstate_dump;
    typeof(cpl_errorstate_get) *errorstate_get;

    typeof(cpl_frame_get_filename) *frame_get_filename;
    typeof(cpl_frame_get_group) *frame_get_group;
    typeof(cpl_frame_get_tag) *frame_get_tag;
    typeof(cpl_frame_new) *frame_new;
    typeof(cpl_frame_set_filename) *frame_set_filename;
    typeof(cpl_frame_set_tag) *frame_set_tag;
    typeof(cpl_frameset_delete) *frameset_delete;
    typeof(cpl_frameset_get_position) *frameset_get_position;
    typeof(cpl_frameset_get_size) *frameset_get_size;
    typeof(cpl_frameset_insert) *frameset_insert;
    typeof(cpl_frameset_new) *frameset_new;

    typeof(cpl_msg_error) *msg_error;
    typeof(cpl_msg_set_level) *msg_set_level;
    typeof(cpl_msg_set_log_level) *msg_set_log_level;
    typeof(cpl_msg_set_log_name) *msg_set_log_name;
    typeof(cpl_msg_stop_log) *msg_stop_log;

    typeof(cpl_parameter_get_alias) *parameter_get_alias;
    typeof(cpl_parameter_get_class) *parameter_get_class;
    typeof(cpl_parameter_get_context) *parameter_get_context;
    typeof(cpl_parameter_get_default_bool) *parameter_get_default_bool;
    typeof(cpl_parameter_get_default_double) *parameter_get_default_double;
    typeof(cpl_parameter_get_default_int) *parameter_get_default_int;
    typeof(cpl_parameter_get_default_string) *parameter_get_default_string;
    typeof(cpl_parameter_get_enum_double) *parameter_get_enum_double;
    typeof(cpl_parameter_get_enum_int) *parameter_get_enum_int;
    typeof(cpl_parameter_get_enum_size) *parameter_get_enum_size;
    typeof(cpl_parameter_get_enum_string) *parameter_get_enum_string;
    typeof(cpl_parameter_get_help) *parameter_get_help;
    typeof(cpl_parameter_get_name) *parameter_get_name;
    typeof(cpl_parameter_get_range_max_double) *parameter_get_range_max_double;
    typeof(cpl_parameter_get_range_max_int) *parameter_get_range_max_int;
    typeof(cpl_parameter_get_range_min_double) *parameter_get_range_min_double;
    typeof(cpl_parameter_get_range_min_int) *parameter_get_range_min_int;
    typeof(cpl_parameter_get_type) *parameter_get_type;
    typeof(cpl_parameter_set_bool) *parameter_set_bool;
    typeof(cpl_parameter_set_double) *parameter_set_double;
    typeof(cpl_parameter_set_int) *parameter_set_int;
    typeof(cpl_parameter_set_string) *parameter_set_string;
    typeof(cpl_parameter_is_enabled) *parameter_is_enabled;
    typeof(cpl_parameterlist_delete) *parameterlist_delete;
    typeof(cpl_parameterlist_find) *parameterlist_find;
    typeof(cpl_parameterlist_get_first) *parameterlist_get_first;
    typeof(cpl_parameterlist_get_next) *parameterlist_get_next;
    typeof(cpl_parameterlist_get_size) *parameterlist_get_size;

    typeof(cpl_recipeconfig_delete) *recipeconfig_delete;
    typeof(cpl_recipeconfig_get_inputs) *recipeconfig_get_inputs;
    typeof(cpl_recipeconfig_get_max_count) *recipeconfig_get_max_count;
    typeof(cpl_recipeconfig_get_min_count) *recipeconfig_get_min_count;
    typeof(cpl_recipeconfig_get_outputs) *recipeconfig_get_outputs;
    typeof(cpl_recipeconfig_get_tags) *recipeconfig_get_tags;
    typeof(cpl_version_get_version) *version_get_version;
    cpl_recipeconfig *(*get_recipeconfig)(cpl_recipe *);
	
    cpl_type TYPE_BOOL;
    cpl_type TYPE_INT;
    cpl_type TYPE_DOUBLE;
    cpl_type TYPE_STRING;
} cpl_library_t;

cpl_library_t *create_library(const char *fname);

#endif /* CPL_LIBRARY_H */
