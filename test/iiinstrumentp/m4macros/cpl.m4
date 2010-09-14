#
# CPL_CREATE_SYMBOLS(build=[])
#-----------------------------
# Sets the Makefile symbols for the CPL and C extension libraries. If an
# argument is provided the symbols are setup for building CPL, if no
# argument is given (default) the symbols are set for using the libraries
# for external package development.
AC_DEFUN([CPL_CREATE_SYMBOLS],
[
    if test -z "$1"; then
        LIBCPLCORE='-lcplcore'
        LIBCPLWCS='-lcplwcs'
        LIBCPLDRS='-lcpldrs'
        LIBCPLUI='-lcplui'
        LIBCPLDFS='-lcpldfs'
    else
        LIBCPLCORE='$(top_builddir)/cplcore/libcplcore.la'
        LIBCPLWCS='$(top_builddir)/cplwcs/libcplwcs.la'
        LIBCPLDRS='$(top_builddir)/cpldrs/libcpldrs.la'
        LIBCPLUI='$(top_builddir)/cplui/libcplui.la'
        LIBCPLDFS='$(top_builddir)/cpldfs/libcpldfs.la'
    fi
   AC_SUBST(LIBCPLCORE)
   AC_SUBST(LIBCPLWCS)
   AC_SUBST(LIBCPLDRS)
   AC_SUBST(LIBCPLUI)
   AC_SUBST(LIBCPLDFS)
])


# CPL_CHECK_LIBS
#---------------
# Checks for the CPL libraries and header files.
AC_DEFUN([CPL_CHECK_LIBS],
[

    AC_MSG_CHECKING([for CPL])

    cpl_check_cpl_header="cpl_macros.h"
    cpl_check_cpl_lib="libcplcore.la"

    cpl_includes=""
    cpl_libraries=""

    AC_ARG_WITH(cpl,
                AC_HELP_STRING([--with-cpl],
                               [location where CPL is installed]),
                [
                    cpl_with_cpl_includes=$withval/include
                    cpl_with_cpl_libs=$withval/lib
                ])

    AC_ARG_WITH(cpl-includes,
                AC_HELP_STRING([--with-cpl-includes],
                               [location of the CPL header files]),
                cpl_with_cpl_includes=$withval)

    AC_ARG_WITH(cpl-libs,
                AC_HELP_STRING([--with-cpl-libs],
                               [location of the CPL library]),
                cpl_with_cpl_libs=$withval)

    AC_ARG_ENABLE(cpl-test,
                  AC_HELP_STRING([--disable-cpl-test],
                                 [disables checks for the CPL library and headers]),
                  cpl_enable_cpl_test=$enableval,
                  cpl_enable_cpl_test=yes)


    if test "x$cpl_enable_cpl_test" = xyes; then

        # Check for the CPL includes

        if test -z "$cpl_with_cpl_includes"; then
            cpl_incdirs="/opt/cpl/include \
                         /usr/local/include \
                         /usr/local/cpl/include \
                         /usr/local/include/cpl \
                         /usr/include/cpl \
                         /usr/include"

            test -n "$CPLDIR" && cpl_incdirs="$CPLDIR/include $cpl_incdirs"
        else
            cpl_incdirs="$cpl_with_cpl_includes"
        fi

        ESO_FIND_FILE($cpl_check_cpl_header, $cpl_incdirs, cpl_includes)


        # Check for the CPL libraries

        if test -z "$cpl_with_cpl_libs"; then
            cpl_libdirs="/opt/cpl/lib \
                         /usr/local/lib \
                         /usr/local/cpl/lib \
                         /usr/lib"

            test -n "$CPLDIR" && cpl_libdirs="$CPLDIR/lib $cpl_libdirs"
        else
            cpl_libdirs="$cpl_with_cpl_libs"
        fi

        ESO_FIND_FILE($cpl_check_cpl_lib, $cpl_libdirs, cpl_libraries)


        if test x"$cpl_includes" = xno || test x"$cpl_libraries" = xno; then
            cpl_notfound=""

            if test x"$cpl_includes" = xno; then
                if test x"$cpl_libraries" = xno; then
                    cpl_notfound="(headers and libraries)"
                else            
                    cpl_notfound="(headers)"
                fi
            else
                cpl_notfound="(libraries)"
            fi

            AC_MSG_ERROR([CPL $cpl_notfound was not found on your system. Please check!])
        else
            AC_MSG_RESULT([libraries $cpl_libraries, headers $cpl_includes])
        fi

        # Set up the symbols

        CPL_INCLUDES="-I$cpl_includes"
        CPL_LDFLAGS="-L$cpl_libraries"

        CPL_CREATE_SYMBOLS
    else
        AC_MSG_RESULT([disabled])
        AC_MSG_WARN([CPL checks have been disabled! This package may not build!])
        CPL_INCLUDES=""
        CPL_LDFLAGS=""
        LIBCPLCORE=""
        LIBCPLWCS=""
        LIBCPLDRS=""
        LIBCPLUI=""
        LIBCPLDFS=""
    fi

    AC_SUBST(CPL_INCLUDES)
    AC_SUBST(CPL_LDFLAGS)
    AC_SUBST(LIBCPLCORE)
    AC_SUBST(LIBCPLWCS)
    AC_SUBST(LIBCPLDRS)
    AC_SUBST(LIBCPLUI)
    AC_SUBST(LIBCPLDFS)

])
