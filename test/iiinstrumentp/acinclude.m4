# IIINSTRUMENT_SET_PREFIX(PREFIX)
#---------------------------
AC_DEFUN([IIINSTRUMENT_SET_PREFIX],
[
    unset CDPATH
    # make $PIPE_HOME the default for the installation
    AC_PREFIX_DEFAULT($1)

    if test "x$prefix" = "xNONE"; then
        prefix=$ac_default_prefix
        ac_configure_args="$ac_configure_args --prefix $prefix"
    fi

    if test "x$exec_prefix" = "xNONE"; then
        exec_prefix=$prefix
    fi

])


# IIINSTRUMENT_SET_VERSION_INFO(VERSION, [CURRENT], [REVISION], [AGE])
#----------------------------------------------------------------
# Setup various version information, especially the libtool versioning
AC_DEFUN([IIINSTRUMENT_SET_VERSION_INFO],
[
    iiinstrument_version=`echo "$1" | sed -e 's/[[a-z,A-Z]].*$//'`

    iiinstrument_major_version=`echo "$iiinstrument_version" | \
        sed 's/\([[0-9]]*\).\(.*\)/\1/'`
    iiinstrument_minor_version=`echo "$iiinstrument_version" | \
        sed 's/\([[0-9]]*\).\([[0-9]]*\)\(.*\)/\2/'`
    iiinstrument_micro_version=`echo "$iiinstrument_version" | \
        sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\3/'`

    if test -z "$iiinstrument_major_version"; then iiinstrument_major_version=0
    fi

    if test -z "$iiinstrument_minor_version"; then iiinstrument_minor_version=0
    fi

    if test -z "$iiinstrument_micro_version"; then iiinstrument_micro_version=0
    fi

    IIINSTRUMENT_VERSION="$iiinstrument_version"
    IIINSTRUMENT_MAJOR_VERSION=$iiinstrument_major_version
    IIINSTRUMENT_MINOR_VERSION=$iiinstrument_minor_version
    IIINSTRUMENT_MICRO_VERSION=$iiinstrument_micro_version

    if test -z "$4"; then IIINSTRUMENT_INTERFACE_AGE=0
    else IIINSTRUMENT_INTERFACE_AGE="$4"
    fi

    IIINSTRUMENT_BINARY_AGE=`expr 100 '*' $IIINSTRUMENT_MINOR_VERSION + $IIINSTRUMENT_MICRO_VERSION`
    IIINSTRUMENT_BINARY_VERSION=`expr 10000 '*' $IIINSTRUMENT_MAJOR_VERSION + \
                          $IIINSTRUMENT_BINARY_AGE`

    AC_SUBST(IIINSTRUMENT_VERSION)
    AC_SUBST(IIINSTRUMENT_MAJOR_VERSION)
    AC_SUBST(IIINSTRUMENT_MINOR_VERSION)
    AC_SUBST(IIINSTRUMENT_MICRO_VERSION)
    AC_SUBST(IIINSTRUMENT_INTERFACE_AGE)
    AC_SUBST(IIINSTRUMENT_BINARY_VERSION)
    AC_SUBST(IIINSTRUMENT_BINARY_AGE)

    AC_DEFINE_UNQUOTED(IIINSTRUMENT_MAJOR_VERSION, $IIINSTRUMENT_MAJOR_VERSION,
                       [IIINSTRUMENT major version number])
    AC_DEFINE_UNQUOTED(IIINSTRUMENT_MINOR_VERSION, $IIINSTRUMENT_MINOR_VERSION,
                       [IIINSTRUMENT minor version number])
    AC_DEFINE_UNQUOTED(IIINSTRUMENT_MICRO_VERSION, $IIINSTRUMENT_MICRO_VERSION,
                       [IIINSTRUMENT micro version number])
    AC_DEFINE_UNQUOTED(IIINSTRUMENT_INTERFACE_AGE, $IIINSTRUMENT_INTERFACE_AGE,
                       [IIINSTRUMENT interface age])
    AC_DEFINE_UNQUOTED(IIINSTRUMENT_BINARY_VERSION, $IIINSTRUMENT_BINARY_VERSION,
                       [IIINSTRUMENT binary version number])
    AC_DEFINE_UNQUOTED(IIINSTRUMENT_BINARY_AGE, $IIINSTRUMENT_BINARY_AGE,
                       [IIINSTRUMENT binary age])

    ESO_SET_LIBRARY_VERSION([$2], [$3], [$4])
])


# IIINSTRUMENT_SET_PATHS
#------------------
# Define auxiliary directories of the installed directory tree.
AC_DEFUN([IIINSTRUMENT_SET_PATHS],
[

    if test -z "$plugindir"; then
        plugindir='${libdir}/${PACKAGE}/plugins/${PACKAGE}-${VERSION}'
    fi

    if test -z "$htmldir"; then
        htmldir='${datadir}/doc/${PACKAGE}/html'
    fi

    if test -z "$configdir"; then
       configdir='${datadir}/${PACKAGE}/config'
    fi

    AC_SUBST(plugindir)
    AC_SUBST(htmldir)
    AC_SUBST(configdir)


    # Define a preprocesor symbol for the plugin search paths

    AC_DEFINE_UNQUOTED(IIINSTRUMENT_PLUGIN_DIR, "${PACKAGE}/plugins",
                       [Plugin directory tree prefix])

    eval plugin_dir="$plugindir"
    plugin_path=`eval echo $plugin_dir | \
                sed -e "s/\/${PACKAGE}-${VERSION}.*$//"`

    AC_DEFINE_UNQUOTED(IIINSTRUMENT_PLUGIN_PATH, "$plugin_path",
                       [Absolute path to the plugin directory tree])

])


# IIINSTRUMENT_CREATE_SYMBOLS
#-----------------------
# Define include and library related makefile symbols
AC_DEFUN([IIINSTRUMENT_CREATE_SYMBOLS],
[

    # Symbols for package include file and library search paths

    IIINSTRUMENT_INCLUDES='-I$(top_srcdir)/iiinstrument'
    IIINSTRUMENT_LDFLAGS='-L$(top_builddir)/iiinstrument'

    all_includes='$(IIINSTRUMENT_INCLUDES) $(CPL_INCLUDES) $(EXTRA_INCLUDES)'
    all_ldflags='$(IIINSTRUMENT_LDFLAGS) $(CPL_LDFLAGS) $(EXTRA_LDFLAGS)'

    # Library aliases

    LIBIIINSTRUMENT='$(top_builddir)/iiinstrument/libiiinstrument.la'

    # Substitute the defined symbols

    AC_SUBST(IIINSTRUMENT_INCLUDES)
    AC_SUBST(IIINSTRUMENT_LDFLAGS)

    AC_SUBST(LIBIIINSTRUMENT)

    # Check for CPL and user defined libraries
    AC_REQUIRE([CPL_CHECK_LIBS])
    AC_REQUIRE([ESO_CHECK_EXTRA_LIBS])

    all_includes='$(IIINSTRUMENT_INCLUDES) $(CPL_INCLUDES) $(EXTRA_INCLUDES)'
    all_ldflags='$(IIINSTRUMENT_LDFLAGS) $(CPL_LDFLAGS) $(EXTRA_LDFLAGS)'

    AC_SUBST(all_includes)
    AC_SUBST(all_ldflags)
])
