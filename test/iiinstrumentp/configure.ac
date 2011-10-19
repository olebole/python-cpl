# Process this file with autoconf to produce a configure script.

AC_INIT([IIINSTRUMENT Instrument Pipeline], [0.0.1], [flastname@eso.org],
[iiinstrument])
AC_PREREQ([2.59])

AC_CONFIG_MACRO_DIR([m4macros])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_AUX_DIR([admin])

AC_CANONICAL_HOST
AC_CANONICAL_TARGET

AM_INIT_AUTOMAKE
AM_CONFIG_HEADER([config.h])

AM_MAINTAINER_MODE

IIINSTRUMENT_SET_PREFIX(${PIPE_HOME:-/usr/local})

# Immediately before every release do:
#-------------------------------------
#   if (the interface is totally unchanged from previous release)
#       REVISION++;
#   else {
#       /* interfaces have been added, removed or changed */
#       REVISION = 0;
#       CURRENT++;
#       if (any interfaces have been _added_ since last release)
#           AGE++;
#       if (any interfaces have been _removed_ or incompatibly changed)
#           AGE = 0;
#   }

IIINSTRUMENT_SET_VERSION_INFO([$VERSION])

# Checks for programs.
AC_PROG_CC
AC_PROG_CPP
AM_PROG_CC_C_O
AC_PROG_LN_S

#
# Check for purify
#
CHECK_PURIFY


ESO_ENABLE_DEBUG(no)
ESO_ENABLE_STRICT(no)
ESO_PROG_CC_FLAG([fno-builtin], [CFLAGS="$CFLAGS -fno-builtin"])
ESO_PROG_CC_FLAG([-std=c99], [CFLAGS="$CFLAGS --std=c99"])

ESO_CHECK_DOCTOOLS

AC_ENABLE_STATIC(no)
AC_ENABLE_SHARED(yes)

AC_PROG_LIBTOOL
AC_SUBST(LIBTOOL_DEPS)

# Checks for libraries.
AC_CHECK_LIB(m, pow, [LIBS="$LIBS -lm"])
AC_CHECK_LIB(socket, socket, [LIBS="$LIBS -lsocket"])
AC_CHECK_LIB(nsl, inet_ntoa, [LIBS="$LIBS -lnsl"])

# Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADERS([string.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_C_CONST
AC_C_INLINE

# Checks for library functions.
AC_CHECK_FUNCS([floor pow sqrt isinf isnan])
ESO_FUNC_STRDUP

# Check for CPL presence and usability
CPL_CHECK_LIBS

IIINSTRUMENT_SET_PATHS
IIINSTRUMENT_CREATE_SYMBOLS

AM_WITH_DMALLOC


AC_CONFIG_FILES(Makefile
                iiinstrument/Makefile
                recipes/Makefile)
AC_OUTPUT
