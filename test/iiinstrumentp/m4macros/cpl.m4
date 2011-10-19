# CPL_CHECK_CFITSIO
#------------------
# Checks for the cfitsio library and header files.
AC_DEFUN([CPL_CHECK_CFITSIO],
[
    cpl_cfitsio_check_header="fitsio.h"
    # FIXME: Check first for the dynamic library...
    cpl_cfitsio_check_lib="libcfitsio.so"

    cpl_cfitsio_dir=""
    cpl_cfitsio_incdirs=""
    cpl_cfitsio_libdirs=""
    cpl_cfitsio_includes=""
    cpl_cfitsio_libraries=""

    # Get the CFITSIO directory from the --with-cfitsio CLI option, or
    # else fall back on the environment variable $CFITSIODIR
    AC_ARG_WITH(cfitsio,
                AC_HELP_STRING([--with-cfitsio],
                               [location where cfitsio is installed]),
                [
                    cpl_cfitsio_dir=$withval
                ],
                [
                    cpl_cfitsio_dir=$CFITSIODIR
                ])

    # Check for the cfitsio includes, either in include/, include/cfitsio/
    # or include/libcfitsio0/
    if test -n "$cpl_cfitsio_dir" ; then
      AC_MSG_CHECKING([for cfitsio in $cpl_cfitsio_dir])
      cpl_cfitsio_incdirs="$cpl_cfitsio_dir/include"
      ESO_FIND_FILE($cpl_cfitsio_check_header, $cpl_cfitsio_incdirs, cpl_cfitsio_includes)
      if test x"$cpl_cfitsio_includes" = xno; then
        # include/cfitsio/ is seen on a 64-bit Fedora 10
        cpl_cfitsio_incdirs="$cpl_cfitsio_dir/include/cfitsio"
        ESO_FIND_FILE($cpl_cfitsio_check_header, $cpl_cfitsio_incdirs, cpl_cfitsio_includes)
        if test x"$cpl_cfitsio_includes" = xno; then
          # include/libcfitsio0/ is seen on a 64-bit Suse
          cpl_cfitsio_incdirs="$cpl_cfitsio_dir/include/libcfitsio0"
          ESO_FIND_FILE($cpl_cfitsio_check_header, $cpl_cfitsio_incdirs, cpl_cfitsio_includes)
        fi
      fi

      # Check for the cfitsio library, either in lib64/, lib32/ or lib/
      cpl_cfitsio_libdirs="$cpl_cfitsio_dir/lib64"
      ESO_FIND_FILE($cpl_cfitsio_check_lib, $cpl_cfitsio_libdirs, cpl_cfitsio_libraries)

      if test x"$cpl_cfitsio_libraries" = xno; then
        cpl_cfitsio_libdirs="$cpl_cfitsio_dir/lib32"
        ESO_FIND_FILE($cpl_cfitsio_check_lib, $cpl_cfitsio_libdirs, cpl_cfitsio_libraries)
        if test x"$cpl_cfitsio_libraries" = xno; then
          cpl_cfitsio_libdirs="$cpl_cfitsio_dir/lib"
          ESO_FIND_FILE($cpl_cfitsio_check_lib, $cpl_cfitsio_libdirs, cpl_cfitsio_libraries)
        fi
      fi

      if test x"$cpl_cfitsio_includes" = xno || test x"$cpl_cfitsio_libraries" = xno; then
          AC_MSG_ERROR([cfitsio was not found on your system. Please check!])
      else
          AC_MSG_RESULT([libraries $cpl_cfitsio_libraries, headers $cpl_cfitsio_includes])
          # Attempt to check the version via CFITSIO_VERSION in the include file
          cpl_cfitsio_check_vers=`perl -nle 's/^#\s*define\s+CFITSIO_VERSION\s+\b// and s/\s.*//, print' $cpl_cfitsio_inclu
des/fitsio.h`
         if test -z "$cpl_cfitsio_check_vers" ; then
           # Attempt to check the version by checking the include files
           cpl_cfitsio_check_vers=`grep "Version Info: This file is distributed with version 2.510 of CFITSIO" $cpl_cfitsio
_includes/fitsio.h`
           if test -z "$cpl_cfitsio_check_vers" ; then
               AC_MSG_WARN([cfitsio version seems to be different from 2.510 and less than 3.X.])
           else
               AC_MSG_WARN([cfitsio version seems to be 2.510])
           fi
         else
            CFLAGS="-D_LARGEFILE_SOURCE=1 -D_FILE_OFFSET_BITS=64 $CFLAGS"
         fi
      fi

      # Set up the symbols
      CFITSIO_INCLUDES="-I$cpl_cfitsio_includes"
      CFITSIO_LDFLAGS="-L$cpl_cfitsio_libraries"
    else
      AC_CHECK_HEADERS($cpl_cfitsio_check_header,,AC_MSG_ERROR([fitsio.h was not found on your system. Please check!]))
      AC_SEARCH_LIBS([fits_get_cwd], [cfitsio],,AC_MSG_ERROR([libcfitsio was not found on your system. Please check!]),[-lpthread])
      CFLAGS="-D_LARGEFILE_SOURCE=1 -D_FILE_OFFSET_BITS=64 $CFLAGS"
    fi

    LIBCFITSIO="-lcfitsio"
    AC_SUBST(CFITSIO_INCLUDES)
    AC_SUBST(CFITSIO_LDFLAGS)
    AC_SUBST(LIBCFITSIO)
])

# CPL_CHECK_WCS
#--------------
# Checks for the wcs library and header files.
AC_DEFUN([CPL_CHECK_WCS],
[
    AC_MSG_CHECKING([for wcs])

    cpl_wcs_check_header="wcslib/wcslib.h"
    cpl_wcs_check_lib="libwcs.a"

    cpl_wcs_includes=""
    cpl_wcs_libraries=""

    AC_ARG_WITH(wcs,
                AC_HELP_STRING([--with-wcs],
                               [location where wcs is installed]),
                [
                    cpl_with_wcs_includes=$withval/include
                    cpl_with_wcs_libs=$withval/lib
                ])

    if test -z "$cpl_with_wcs_includes"; then
        test -n "$WCSDIR" && cpl_wcs_incdirs="$WCSDIR/include"
    else
        cpl_wcs_incdirs="$cpl_with_wcs_includes"
    fi

    if test -z "$cpl_with_wcs_libs"; then
        test -n "$WCSDIR" && cpl_wcs_libdirs="$WCSDIR/lib"
    else
        cpl_wcs_libdirs="$cpl_with_wcs_libs"
    fi

    if test -n "$cpl_with_wcs_includes"; then
      # Check for the wcs includes
      ESO_FIND_FILE($cpl_wcs_check_header, $cpl_wcs_incdirs, cpl_wcs_includes)
    else
      AC_CHECK_HEADERS($cpl_wcs_check_header,,cpl_wcs_includes="no")
    fi

    # Check for the wcs library
    if test -n "$cpl_with_wcs_libs"; then
      ESO_FIND_FILE($cpl_wcs_check_lib, $cpl_wcs_libdirs, cpl_wcs_libraries)
    else
      AC_SEARCH_LIBS([wcsini], [wcs],,cpl_wcs_libraries="no",)
    fi

    if test x"$cpl_wcs_includes" = xno || test x"$cpl_wcs_libraries" = xno; then
        AC_MSG_WARN([wcs was not found on your system.])
    else
        AC_MSG_RESULT([libraries $cpl_wcs_libraries, headers $cpl_wcs_includes])
        if test -n "$cpl_wcs_includes" ; then
          # Attempt to check the version by checking the include files
          cpl_wcs_check_vers43=`grep "WCSLIB 4.3 - an implementation of the FITS WCS standard" $cpl_wcs_includes/wcslib/wcslib.h`
          if test -z "$cpl_wcs_check_vers43" ; then
              cpl_wcs_check_vers44=`grep "WCSLIB 4.4 - an implementation of the FITS WCS standard" $cpl_wcs_includes/wcslib/wcslib.h`
              if test -z "$cpl_wcs_check_vers44" ; then
                  AC_MSG_WARN([wcs version seems to be older than 4.3])
              fi
          fi
        fi
        AC_DEFINE_UNQUOTED(CPL_WCS_INSTALLED, 1, [Defined if WCS is available])
        # Set up the symbols
        if test -n "$cpl_wcs_includes" ; then
          WCS_INCLUDES="-I$cpl_wcs_includes"
        fi
        if test -n "$cpl_wcs_libraries" ; then
          WCS_LDFLAGS="-L$cpl_wcs_libraries"
        fi
        LIBWCS="-lwcs"

        AC_SUBST(WCS_INCLUDES)
        AC_SUBST(WCS_LDFLAGS)
        AC_SUBST(LIBWCS)
    fi
])

# CPL_CHECK_FFTW
#--------------
# Checks for the wcs library and header files.
AC_DEFUN([CPL_CHECK_FFTW],
[
    AC_MSG_CHECKING([for fftw])

    cpl_fftw_check_header="fftw3.h"
    cpl_fftwf_check_header="fftw3.h"
    cpl_fftw_check_lib="libfftw3.a"
    cpl_fftwf_check_lib="libfftw3f.a"

    cpl_fftw_includes=""
    cpl_fftwf_includes=""
    cpl_fftw_libraries=""
    cpl_fftwf_libraries=""

    AC_ARG_WITH(fftw,
                AC_HELP_STRING([--with-fftw],
                               [location where fftw is installed]),
                [
                    cpl_with_fftw_includes=$withval/include
                    cpl_with_fftw_libs=$withval/lib
                ])

    if test -z "$cpl_with_fftw_includes"; then
        test -n "$FFTWDIR" && cpl_fftw_incdirs="$FFTWDIR/include"
    else
        cpl_fftw_incdirs="$cpl_with_fftw_includes"
    fi
    if test -z "$cpl_with_fftw_libs"; then
        test -n "$FFTWDIR" && cpl_fftw_libdirs="$FFTWDIR/lib"
    else
        cpl_fftw_libdirs="$cpl_with_fftw_libs"
    fi

    # Check for the fftw includes
    if test -n "$cpl_fftw_incdirs"; then
      ESO_FIND_FILE($cpl_fftw_check_header, $cpl_fftw_incdirs, cpl_fftw_includes)
      ESO_FIND_FILE($cpl_fftwf_check_header, $cpl_fftw_incdirs, cpl_fftwf_includes)
    else
      AC_CHECK_HEADERS($cpl_fftw_check_header,,cpl_fftw_includes="no")
      AC_CHECK_HEADERS($cpl_fftwf_check_header,,cpl_fftwf_includes="no")
    fi

    # Check for the fftw library
    if test -n "$cpl_fftw_libdirs"; then
      ESO_FIND_FILE($cpl_fftw_check_lib, $cpl_fftw_libdirs, cpl_fftw_libraries)
      ESO_FIND_FILE($cpl_fftwf_check_lib, $cpl_fftw_libdirs, cpl_fftwf_libraries)
    else
      AC_SEARCH_LIBS([fftw_version], [fftw3],,cpl_fftw_libraries="no",)
      AC_SEARCH_LIBS([fftwf_version], [fftw3f],,cpl_fftwf_libraries="no",)
    fi

    if test x"$cpl_fftw_includes" = xno || test x"$cpl_fftw_libraries" = xno; then
        AC_MSG_WARN([fftw (normal-precision) was not found on your system.])
    else
        AC_MSG_RESULT([libraries $cpl_fftw_libraries, headers $cpl_fftw_includes])
        # FIXME: Attempt to check the version

        AC_DEFINE_UNQUOTED(CPL_FFTW_INSTALLED, 1, [Defined if FFTW (normal-precision) is available])
        # Set up the symbols
        if test -n "$cpl_fftw_includes"; then
          FFTW_INCLUDES="-I$cpl_fftw_includes"
        fi
        if test -n "$cpl_fftw_libraries"; then
          FFTW_LDFLAGS="-L$cpl_fftw_libraries"
        fi
        LIBFFTW="-lfftw3"

        AC_SUBST(FFTW_INCLUDES)
        AC_SUBST(FFTW_LDFLAGS)
        AC_SUBST(LIBFFTW)
    fi

    if test x"$cpl_fftwf_includes" = xno || test x"$cpl_fftwf_libraries" = xno; then
        AC_MSG_WARN([fftw (single-precision) was not found on your system.])
    else
        AC_MSG_RESULT([libraries $cpl_fftwf_libraries, headers $cpl_fftwf_includes])
        # FIXME: Attempt to check the version

        AC_DEFINE_UNQUOTED(CPL_FFTWF_INSTALLED, 1, [Defined if FFTW (single-precision) is available])
        # Set up the symbols
        if test -n "$cpl_fftwf_includes"; then
          FFTWF_INCLUDES="-I$cpl_fftwf_includes"
        fi
        if test -n "$cpl_fftwf_libraries"; then
          FFTWF_LDFLAGS="-L$cpl_fftwf_libraries"
        fi
        LIBFFTWF="-lfftw3f"

        AC_SUBST(FFTWF_INCLUDES)
        AC_SUBST(FFTWF_LDFLAGS)
        AC_SUBST(LIBFFTWF)
    fi

])

#
# CPL_CREATE_SYMBOLS(build=[])
#-----------------------------
# Sets the Makefile symbols for the CPL libraries. If an argument is
# provided the symbols are setup for building CPL, if no argument is
# given (default) the symbols are set for using the libraries
# for external package development.
AC_DEFUN([CPL_CREATE_SYMBOLS],
[

    if test -z "$1"; then
        LIBCPLCORE='-lcplcore'
        LIBCPLDRS='-lcpldrs'
        LIBCPLUI='-lcplui'
        LIBCPLDFS='-lcpldfs'
    else
        LIBCPLCORE='$(top_builddir)/cplcore/libcplcore.la'
        LIBCPLDRS='$(top_builddir)/cpldrs/libcpldrs.la'
        LIBCPLUI='$(top_builddir)/cplui/libcplui.la'
        LIBCPLDFS='$(top_builddir)/cpldfs/libcpldfs.la'
    fi

   AC_SUBST(LIBCPLCORE)
   AC_SUBST(LIBCPLDRS)
   AC_SUBST(LIBCPLUI)
   AC_SUBST(LIBCPLDFS)

])


# CPL_CHECK_LIBS
#---------------
# Checks for the CPL libraries and header files.
AC_DEFUN([CPL_CHECK_LIBS],
[

    AC_REQUIRE([CPL_CHECK_CFITSIO])
    
    cpl_check_cpl_header="cpl.h"
    cpl_check_cpl_lib="libcplcore.so"

    cpl_incdirs=""
    cpl_libdirs=""
    cpl_includes=""
    cpl_libraries=""

    AC_ARG_WITH(cpl,
                AC_HELP_STRING([--with-cpl],
                               [location where CPL is installed]),
                [
                    cpl_with_cpl=$withval
                ])

    if test -n "$cpl_with_cpl" ; then
      AC_MSG_CHECKING([for CPL])
      cpl_incdirs="$cpl_with_cpl/include"
      ESO_FIND_FILE($cpl_check_cpl_header, $cpl_incdirs, cpl_includes)
        
      cpl_libdirs="$cpl_with_cpl/lib"
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
          # Set up the symbols

          CPL_INCLUDES="-I$cpl_includes"
          CPL_LDFLAGS="-L$cpl_libraries"
      fi
    else
       AC_CHECK_HEADERS($cpl_check_cpl_header,,AC_MSG_ERROR([cpl.h was not found on your system. Please check!]))
       AC_SEARCH_LIBS([cpl_init], [cplcore],,AC_MSG_ERROR([libcplcore was not found on your system. Please check!]),)
    fi

    CPL_CREATE_SYMBOLS
     AC_SUBST(CPL_INCLUDES)
    AC_SUBST(CPL_LDFLAGS)
    AC_SUBST(LIBCPLCORE)
    AC_SUBST(LIBCPLDRS)
    AC_SUBST(LIBCPLUI)
    AC_SUBST(LIBCPLDFS)

])
