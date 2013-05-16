/*

 This header file is compiled from the original CPL header files to contain
 just the functions and macros that we need in the framework.
 
 Since it is mainly copied and pasted, here is the original license
 statement from /usr/include/cpl.h:
 
 * Id: cpl.h,v 1.31 2009/12/02 10:29:45 lbilbao Exp
 *
 * This file is part of the ESO Common Pipeline Library
 * Copyright (C) 2001-2008 European Southern Observatory
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
#ifndef CPL_API_H
#define CPL_API_H

#define CPL_VERSION(major, minor, micro) \
        (((major) * 65536) + ((minor) * 256) + (micro))

#define CPL_VERSION_MAJOR_CODE(code) (((code) >> 16) & 0xff)
#define CPL_VERSION_MINOR_CODE(code) (((code) >> 8) & 0xff)
#define CPL_VERSION_MICRO_CODE(code) ((code) & 0xff)

#define CPL_VERSION_CODE CPL_VERSION(6,3,0)

typedef int cpl_error_code, cpl_errorstate, cpl_boolean, cpl_frame_group,
    cpl_parameter_mode, cpl_parameter_class, cpl_type, cpl_msg_severity;
typedef long long cpl_size;
typedef void cpl_pluginlist, cpl_frameset, cpl_frame, 
    cpl_parameter, cpl_parameterlist, cpl_recipeconfig;

typedef struct _cpl_plugin_ cpl_plugin;
typedef int (*cpl_plugin_func)(cpl_plugin *);
struct _cpl_plugin_ {
    unsigned int api;
    unsigned long version;
    unsigned long type;
    const char *name;
    const char *synopsis;
    const char *description;
    const char *author;
    const char *email;
    const char *copyright;
    cpl_plugin_func initialize;
    cpl_plugin_func execute;
    cpl_plugin_func deinitialize;
};

struct _cpl_recipe_ {
    cpl_plugin interface;
    cpl_parameterlist *parameters;
    cpl_frameset *frames;
};
typedef struct _cpl_recipe_ cpl_recipe;

unsigned int cpl_version_get_major(void);
unsigned int cpl_version_get_minor(void);
unsigned int cpl_version_get_micro(void);

void cpl_init(unsigned);
void cpl_end(void);
const char * cpl_get_description(unsigned);
int cpl_memory_is_empty(void);
void cpl_memory_dump(void);
void cpl_free(void *);
const char *cpl_plugin_get_author(const cpl_plugin *self);
const char *cpl_plugin_get_copyright(const cpl_plugin *self);
cpl_plugin_func cpl_plugin_get_deinit(const cpl_plugin *self);
const char *cpl_plugin_get_description(const cpl_plugin *self);
const char *cpl_plugin_get_email(const cpl_plugin *self);
cpl_plugin_func cpl_plugin_get_exec(const cpl_plugin *self);
cpl_plugin_func cpl_plugin_get_init(const cpl_plugin *self);
const char *cpl_plugin_get_name(const cpl_plugin *self);
const char *cpl_plugin_get_synopsis(const cpl_plugin *self);
unsigned long cpl_plugin_get_version(const cpl_plugin *self);
char *cpl_plugin_get_version_string(const cpl_plugin *self);
void cpl_pluginlist_delete(cpl_pluginlist *);
cpl_plugin *cpl_pluginlist_find(cpl_pluginlist *, const char *);
cpl_plugin *cpl_pluginlist_get_first(cpl_pluginlist *);
cpl_plugin *cpl_pluginlist_get_next(cpl_pluginlist *);
cpl_pluginlist *cpl_pluginlist_new(void);
cpl_error_code cpl_dfs_update_product_header(cpl_frameset *);

void cpl_msg_error(const char *, const char *, ...);
cpl_error_code cpl_error_get_code(void);
const char *cpl_error_get_file(void);
const char *cpl_error_get_function(void);
unsigned cpl_error_get_line(void);
const char *cpl_error_get_message(void);
void cpl_error_reset(void);
cpl_error_code
cpl_error_set_message_macro(const char *, cpl_error_code,
                            const char *, unsigned,
                            const char *, ...);
void cpl_errorstate_dump(cpl_errorstate,
                         cpl_boolean,
                         void (*)(unsigned, unsigned, unsigned));
cpl_errorstate cpl_errorstate_get(void);

const char *cpl_frame_get_filename(const cpl_frame *self);
cpl_frame_group cpl_frame_get_group(const cpl_frame *self);
const char *cpl_frame_get_tag(const cpl_frame *self);
cpl_frame *cpl_frame_new(void);
cpl_error_code cpl_frame_set_filename(cpl_frame *self, const char *filename);
cpl_error_code cpl_frame_set_tag(cpl_frame *self, const char *tag);

void cpl_frameset_delete(cpl_frameset *self);
cpl_frame *cpl_frameset_get_position(cpl_frameset *self, cpl_size position);
cpl_size cpl_frameset_get_size(const cpl_frameset *self);
cpl_error_code cpl_frameset_insert(cpl_frameset *self, cpl_frame *frame);
cpl_frameset *cpl_frameset_new(void);
void cpl_msg_set_level(cpl_msg_severity);
cpl_error_code cpl_msg_set_log_level(cpl_msg_severity);
cpl_error_code cpl_msg_set_log_name(const char *);
cpl_error_code cpl_msg_stop_log(void);

const char *cpl_parameter_get_alias(const cpl_parameter *self,
                                    cpl_parameter_mode mode);
cpl_parameter_class cpl_parameter_get_class(const cpl_parameter *self);
const char *cpl_parameter_get_context(const cpl_parameter *self);
int cpl_parameter_get_default_bool(const cpl_parameter *self);
int cpl_parameter_get_default_int(const cpl_parameter *self);
double cpl_parameter_get_default_double(const cpl_parameter *self);
const char *cpl_parameter_get_default_string(const cpl_parameter *self);
int cpl_parameter_get_enum_size(const cpl_parameter *self);
int cpl_parameter_get_enum_int(const cpl_parameter *self, int position);
double cpl_parameter_get_enum_double(const cpl_parameter *self, int position);
const char *cpl_parameter_get_enum_string(const cpl_parameter *self,
                                          int position);
const char *cpl_parameter_get_help(const cpl_parameter *self);
const char *cpl_parameter_get_name(const cpl_parameter *self);
int cpl_parameter_get_range_min_int(const cpl_parameter *self);
double cpl_parameter_get_range_min_double(const cpl_parameter *self);
int cpl_parameter_get_range_max_int(const cpl_parameter *self);
double cpl_parameter_get_range_max_double(const cpl_parameter *self);
cpl_type cpl_parameter_get_type(const cpl_parameter *self);
cpl_error_code cpl_parameter_set_bool(cpl_parameter *self, int value);
cpl_error_code cpl_parameter_set_int(cpl_parameter *self, int value);
cpl_error_code cpl_parameter_set_double(cpl_parameter *self, double value);
cpl_error_code cpl_parameter_set_string(cpl_parameter *self,
                                        const char *value);
int cpl_parameter_is_enabled(const cpl_parameter *self,
                             cpl_parameter_mode mode);
void cpl_parameterlist_delete(cpl_parameterlist *self);
cpl_parameter *cpl_parameterlist_find(cpl_parameterlist *self,
                                      const char *name);
cpl_parameter *cpl_parameterlist_get_first(cpl_parameterlist *self);
cpl_parameter *cpl_parameterlist_get_next(cpl_parameterlist *self);
cpl_size cpl_parameterlist_get_size(const cpl_parameterlist *self);

void cpl_recipeconfig_delete(const cpl_recipeconfig* self);
char** cpl_recipeconfig_get_inputs(const cpl_recipeconfig* self,
                                   const char* tag);
cpl_size cpl_recipeconfig_get_min_count(const cpl_recipeconfig* self,
                                        const char* tag, const char* input);
cpl_size cpl_recipeconfig_get_max_count(const cpl_recipeconfig* self,
                                        const char* tag, const char* input);
char** cpl_recipeconfig_get_outputs(const cpl_recipeconfig* self,
                                    const char* tag);
char** cpl_recipeconfig_get_tags(const cpl_recipeconfig* self);
const char *cpl_version_get_version(void);


#define CPL_INIT_DEFAULT 0
#define CPL_DESCRIPTION_DEFAULT 0
#define CPL_MSG_OFF 4
#define CPL_FALSE 0
#define CPL_ERROR_NONE 0
#define CPL_ERROR_FILE_NOT_CREATED 8
#define CPL_FRAME_GROUP_PRODUCT 3
#define CPL_PARAMETER_CLASS_ENUM (1 << 3)
#define CPL_PARAMETER_CLASS_RANGE (1 << 2)
#define CPL_PARAMETER_MODE_CLI (1 << 0)
#define CPL_PARAMETER_MODE_ENV (1 << 1)
#define CPL_PARAMETER_MODE_CFG (1 << 2)
#define CPL_TYPE_BOOL (1 << 7)
#define CPL_TYPE_DOUBLE (1 << 17)
#define CPL_TYPE_INT (1 << 10)
#define CPL_TYPE_STRING ((1 << 5)|(1 << 0))

#endif /* CPL_API_H */
