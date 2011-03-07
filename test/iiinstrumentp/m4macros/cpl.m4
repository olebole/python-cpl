# CPL_CHECK_CFITSIO
#------------------
# Checks for the cfitsio library and header files.
AC_DEFUN([CPL_CHECK_CFITSIO],
[

    AC_REQUIRE([ESO_CHECK_THREADS_POSIX])
        
    cpl_cfitsio_check_header="fitsio.h"
    cpl_cfitsio_check_lib="libcfitsio.a"

    cpl_cfitsio_incdirs=""
    cpl_cfitsio_libdirs=""
    cpl_cfitsio_includes=""
    cpl_cfitsio_libraries=""

    AC_ARG_WITH(cfitsio,
                AC_HELP_STRING([--with-cfitsio],
                               [location where cfitsio is installed]),
                [
                    cpl_with_cfitsio=$withval
                ])

    AC_ARG_WITH(cfitsio-includes,
                AC_HELP_STRING([--with-cfitsio-includes],
                               [location of the cfitsio header files]),
                cpl_with_cfitsio_includes=$withval)

    AC_ARG_WITH(cfitsio-libs,
                AC_HELP_STRING([--with-cfitsio-libs],
                               [location of the cfitsio library]),
                cpl_with_cfitsio_libs=$withval)

    AC_ARG_ENABLE(cfitsio-test,
                  AC_HELP_STRING([--disable-cfitsio-test],
                                 [disables checks for the cfitsio library and headers]),
                  cpl_enable_cfitsio_test=$enableval,
                  cpl_enable_cfitsio_test=yes)


    # We need libpthread for the folloing tests

    if test -z "$LIBPTHREAD"; then
        AC_MSG_ERROR([POSIX thread library was not found on your system! Please check!])
    fi

    
    AC_MSG_CHECKING([for cfitsio])

    if test "x$cpl_enable_cfitsio_test" = xyes; then

        # Check for the cfitsio includes

        if test -z "$cpl_with_cfitsio_includes"; then
        
            if test -z "$cpl_with_cfitsio"; then
            
                # Try some known system locations
                
                cpl_cfitsio_incdirs="/opt/cfitsio/include"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs /usr/local/include/libcfitsio0"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs /usr/local/include/cfitsio"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs /usr/local/include"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs /usr/include/libcfitsio0"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs /usr/include/cfitsio"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs /usr/include"

                test -n "$CFITSIODIR" && \ 
                    cpl_cfitsio_incdirs="$CFITSIODIR/include/libcfitsio0 \
                                         $CFITSIODIR/include/cfitsio \
                                         $CFITSIODIR/include \
                                         $cpl_cfitsio_incdirs"

                test -n "$CPLDIR" && \
                    cpl_cfitsio_incdirs="$CPLDIR/include/libcfitsio0 \
                                         $CPLDIR/include/cfitsio \
                                         $CPLDIR/include \
                                         $cpl_cfitsio_incdirs"

            else

                cpl_cfitsio_incdirs="$cpl_with_cfitsio/include/libcfitsio0"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs $cpl_with_cfitsio/include/cfitsio"
                cpl_cfitsio_incdirs="$cpl_cfitsio_incdirs $cpl_with_cfitsio/include"

            fi
            
        else
            cpl_cfitsio_incdirs="$cpl_with_cfitsio_includes"
        fi

        ESO_FIND_FILE($cpl_cfitsio_check_header, $cpl_cfitsio_incdirs,
                      cpl_cfitsio_includes)


        # Check for the cfitsio library

        if test -z "$cpl_with_cfitsio_libs"; then

            if test -z "$cpl_with_cfitsio"; then
            
                # Try some known system locations

                cpl_cfitsio_libdirs="/opt/cfitsio/lib"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs /usr/local/lib64"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs /usr/local/lib"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs /usr/local/lib32"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs /usr/lib64"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs /usr/lib"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs /usr/lib32"

                test -n "$CFITSIODIR" && \
                    cpl_cfitsio_libdirs="$CFITSIODIR/lib64 $CFITSIODIR/lib \
                                         $CFITSIODIR/lib $cpl_cfitsio_libdirs"

                test -n "$CPLDIR" && \
                    cpl_cfitsio_libdirs="$CPLDIR/lib64 $CPLDIR/lib $CPLDIR/lib32 \
                                         $cpl_cfitsio_libdirs"

            else

                cpl_cfitsio_libdirs="$cpl_with_cfitsio/lib64"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs $cpl_with_cfitsio/lib"
                cpl_cfitsio_libdirs="$cpl_cfitsio_libdirs $cpl_with_cfitsio/lib32"

            fi
            
        else
            cpl_cfitsio_libdirs="$cpl_with_cfitsio_libs"
        fi

        ESO_FIND_FILE($cpl_cfitsio_check_lib, $cpl_cfitsio_libdirs,
                      cpl_cfitsio_libraries)


        if test x"$cpl_cfitsio_includes" = xno || \
            test x"$cpl_cfitsio_libraries" = xno; then
            cpl_cfitsio_notfound=""

            if test x"$cpl_cfitsio_includes" = xno; then
                if test x"$cpl_cfitsio_libraries" = xno; then
                    cpl_cfitsio_notfound="(headers and libraries)"
                else
                    cpl_cfitsio_notfound="(headers)"
                fi
            else
                cpl_cfitsio_notfound="(libraries)"
            fi

            AC_MSG_ERROR([cfitsio $cpl_cfitsio_notfound was not found on your system. Please check!])
        else
            AC_MSG_RESULT([libraries $cpl_cfitsio_libraries, headers $cpl_cfitsio_includes])
        fi

        # Set up the symbols

        CFITSIO_INCLUDES="-I$cpl_cfitsio_includes"
        CFITSIO_LDFLAGS="-L$cpl_cfitsio_libraries"
        LIBCFITSIO="-lcfitsio"

        # Do not add redundant libraries        
        echo $LIBS | grep -q -e '-lm' || LIBS="-lm $LIBS" 
        

        # Check whether cfitsio can be used

        AC_MSG_CHECKING([whether cfitsio can be used])
        AC_LANG_PUSH(C)
        
        cpl_cfitsio_cflags_save="$CFLAGS"
        cpl_cfitsio_ldflags_save="$LDFLAGS"
        cpl_cfitsio_libs_save="$LIBS"

        CFLAGS="$CFITSIO_INCLUDES"
        LDFLAGS="$CFITSIO_LDFLAGS"
        LIBS="$LIBCFITSIO $LIBPTHREAD -lm"
        
        AC_LINK_IFELSE([AC_LANG_PROGRAM(
                       [[
                       #include <fitsio.h>
                       ]],
                       [
                       float v;
                       fits_get_version(&v);
                       ])],
                       [cpl_cfitsio_is_usable="yes"],
                       [cpl_cfitsio_is_usable="no"])

        AC_MSG_RESULT([$cpl_cfitsio_is_usable])
        
        AC_LANG_POP(C)
        
        CFLAGS="$cpl_cfitsio_cflags_save"
        LDFLAGS="$cpl_cfitsio_ldflags_save"
        LIBS="$cpl_cfitsio_libs_save"

        if test x"$cpl_cfitsio_is_usable" = xno; then
            AC_MSG_ERROR([Linking with cfitsio failed! Please check architecture!])
        fi
 
        
        # Check cfitsio version

        AC_MSG_CHECKING([for a cfitsio version >= 3.0])
        
        AC_LANG_PUSH(C)
        
        cpl_cfitsio_cflags_save="$CFLAGS"
        cpl_cfitsio_ldflags_save="$LDFLAGS"
        cpl_cfitsio_libs_save="$LIBS"

        CFLAGS="$CFITSIO_INCLUDES"
        LDFLAGS="$CFITSIO_LDFLAGS"
        LIBS="$LIBCFITSIO $LIBPTHREAD -lm"
        
        AC_RUN_IFELSE([AC_LANG_PROGRAM(
                      [[
                      #include <stdio.h>
                      #include <fitsio.h>
                      ]],
                      [
                      float v;
                      
                      fits_get_version(&v);
                      if (v >= 3.0) {
                          FILE* f = fopen("conftest.out", "w");
                          fprintf(f, "%5.3f\n", v);
                          fclose(f);
                          return 0;
                      }
                      return 1;
                      ])],
                      [cpl_cfitsio_version="`cat conftest.out`"],
                      [cpl_cfitsio_version="no"])

        AC_MSG_RESULT([$cpl_cfitsio_version])
        
        AC_LANG_POP(C)
        
        CFLAGS="$cpl_cfitsio_cflags_save"
        LDFLAGS="$cpl_cfitsio_ldflags_save"
        LIBS="$cpl_cfitsio_libs_save"

        if test x"$cpl_cfitsio_is_usable" = xno; then
            AC_MSG_ERROR([Linking with cfitsio failed! Please check architecture!])
        fi
 
        
        # Check whether cfitsio has large file support
        
        AC_LANG_PUSH(C)
        
        cpl_cfitsio_cflags_save="$CFLAGS"
        cpl_cfitsio_ldflags_save="$LDFLAGS"
        cpl_cfitsio_libs_save="$LIBS"

        CFLAGS="$CFITSIO_INCLUDES"
        LDFLAGS="$CFITSIO_LDFLAGS"
        LIBS="$LIBCFITSIO -lm $LIBPTHREAD"
        
        AC_MSG_CHECKING([whether cfitsio provides fits_hdu_getoff()])

        AC_COMPILE_IFELSE([AC_LANG_PROGRAM(
                          [[
                          #include <fitsio.h>
                          ]],
                          [
                          fitsfile f;
                          int sts;
                          fits_get_hduoff(&f, NULL, NULL, NULL, &sts);
                          ])],
                          [cpl_cfitsio_have_fits_get_hduoff="yes"],
                          [cpl_cfitsio_have_fits_get_hduoff="no"])

        AC_MSG_RESULT([$cpl_cfitsio_have_fits_get_hduoff])
        
        AC_MSG_CHECKING([whether cfitsio provides fits_get_hduaddrll()])

        AC_COMPILE_IFELSE([AC_LANG_PROGRAM(
                          [[
                          #include <fitsio.h>
                          ]],
                          [
                          fitsfile f;
                          int sts;
                          fits_get_hduaddrll(&f, NULL, NULL, NULL, &sts);
                          ])],
                          [cpl_cfitsio_have_fits_get_hduaddrll="yes"],
                          [cpl_cfitsio_have_fits_get_hduaddrll="no"])

        AC_MSG_RESULT([$cpl_cfitsio_have_fits_get_hduaddrll])

        AC_LANG_POP(C)
        
        CFLAGS="$cpl_cfitsio_cflags_save"
        LDFLAGS="$cpl_cfitsio_ldflags_save"
        LIBS="$cpl_cfitsio_libs_save"


        # Check whether cfitsio is thread-safe
        
        AC_MSG_CHECKING([whether cfitsio requires libpthread])
        AC_LANG_PUSH(C)
        
        cpl_cfitsio_cflags_save="$CFLAGS"
        cpl_cfitsio_ldflags_save="$LDFLAGS"
        cpl_cfitsio_libs_save="$LIBS"

        CFLAGS="$CFITSIO_INCLUDES"
        LDFLAGS="$CFITSIO_LDFLAGS"
        LIBS="$LIBCFITSIO -lm"
        
        AC_LINK_IFELSE([AC_LANG_PROGRAM(
                       [[
                       #include <fitsio.h>
                       ]],
                       [
                       float v;
                       fits_get_version(&v);
                       ])],
                       [cpl_cfitsio_requires_pthread="no"],
                       [cpl_cfitsio_requires_pthread="undefined"])

        if test x"$cpl_cfitsio_requires_pthread" != xno; then
        
            LIBS="$LIBCFITSIO -lm $LIBPTHREAD"
        
            AC_LINK_IFELSE([AC_LANG_PROGRAM(
                           [[
                           #include <fitsio.h>
                           ]],
                           [
                           float v;
                           fits_get_version(&v);
                           ])],
                           [cpl_cfitsio_requires_pthread="yes"],
                           AC_MSG_FAILURE([Cannot link with cfitsio! Please check!]))
          
        fi
                       
        AC_MSG_RESULT([$cpl_cfitsio_requires_pthread])
        
        AC_LANG_POP(C)
        
        CFLAGS="$cpl_cfitsio_cflags_save"
        LDFLAGS="$cpl_cfitsio_ldflags_save"
        LIBS="$cpl_cfitsio_libs_save"


        # Set compiler flags and libraries
        
        if test x"$cpl_cfitsio_have_fits_get_hduoff" = xyes || \
          test x"$cpl_cfitsio_have_fits_get_hduaddrll" = xyes; then

            CFLAGS="-D_LARGEFILE_SOURCE=1 -D_FILE_OFFSET_BITS=64 $CFLAGS"
            
            if test x"$cpl_cfitsio_have_fits_get_hduoff"; then
                AC_DEFINE([HAVE_FITS_GET_HDUOFF], [1],
                          [Define if you have the `fits_get_hduoff' function])
            else
                AC_DEFINE([HAVE_FITS_GET_HDUADDRLL],  [1],
                          [Define if you have the `fits_get_hduaddrll' function])
            fi
                    
        fi
                
        if test x"$cpl_cfitsio_requires_pthread" = xyes; then
            echo $LIBS | grep -q -e "$LIBPTHREAD" || LIBS="$LIBPTHREAD $LIBS"
        fi
        
    else
        AC_MSG_RESULT([disabled])
        AC_MSG_WARN([cfitsio checks have been disabled! This package may not build!])
        CFITSIO_INCLUDES=""
        CFITSIO_LDFLAGS=""
        LIBCFITSIO=""
        
        cpl_cfitsio_requires_pthread="undefined"
    fi

	AC_CACHE_VAL(cpl_cv_cfitsio_requires_pthread,
	             cpl_cv_cfitsio_requires_pthread=$cpl_cfitsio_requires_pthread)
	             
    AC_SUBST(CFITSIO_INCLUDES)
    AC_SUBST(CFITSIO_LDFLAGS)
    AC_SUBST(LIBCFITSIO)

])


# CPL_CHECK_CEXT
#---------------
# Checks for the C extension library and header files.
AC_DEFUN([CPL_CHECK_CEXT],
[

    AC_MSG_CHECKING([for libcext])

    cpl_cext_check_header="cxtypes.h"
    cpl_cext_check_lib="libcext.a"

    cpl_cext_incdirs=""
    cpl_cext_libdirs=""
    cpl_cext_includes=""
    cpl_cext_libraries=""

    AC_ARG_WITH(cext,
                AC_HELP_STRING([--with-cext],
                               [location where libcext is installed]),
                [
                    cpl_with_cext=$withval
                ])

    AC_ARG_WITH(cext-includes,
                AC_HELP_STRING([--with-cext-includes],
                               [location of the libcext header files]),
                cpl_with_cext_includes=$withval)

    AC_ARG_WITH(cext-libs,
                AC_HELP_STRING([--with-cext-libs],
                               [location of the libcext library]),
                cpl_with_cext_libs=$withval)

    AC_ARG_ENABLE(cext-test,
                  AC_HELP_STRING([--disable-cext-test],
                                 [disables checks for the libcext library and headers]),
                  cpl_enable_cext_test=$enableval,
                  cpl_enable_cext_test=yes)


    if test "x$cpl_enable_cext_test" = xyes; then

        # Check for the libcext includes

        if test -z "$cpl_with_cext_includes"; then
        
            if test -z "$cpl_with_cext"; then
            
                # Try some known system locations
                
                cpl_cext_incdirs="/opt/cext/include"
                cpl_cext_incdirs="$cpl_cext_incdirs /usr/local/include/cext"
                cpl_cext_incdirs="$cpl_cext_incdirs /usr/local/include"
                cpl_cext_incdirs="$cpl_cext_incdirs /usr/include/cext"
                cpl_cext_incdirs="$cpl_cext_incdirs /usr/include"

                test -n "$CPLDIR" && \
                    cpl_cext_incdirs="$CPLDIR/include/cext \
                                      $CPLDIR/include \
                                      $cpl_cext_incdirs"

            else

                cpl_cext_incdirs="$cpl_with_cext/include/cext"
                cpl_cext_incdirs="$cpl_cext_incdirs $cpl_with_cext/include"

            fi
            
        else
            cpl_cext_incdirs="$cpl_with_cext_includes"
        fi

        ESO_FIND_FILE($cpl_cext_check_header, $cpl_cext_incdirs,
                      cpl_cext_includes)


        # Check for the libcext library

        if test -z "$cpl_with_cext_libs"; then

            if test -z "$cpl_with_cext"; then
            
                # Try some known system locations

                cpl_cext_libdirs="/opt/cext/lib"
                cpl_cext_libdirs="$cpl_cext_libdirs /usr/local/lib64"
                cpl_cext_libdirs="$cpl_cext_libdirs /usr/local/lib"
                cpl_cext_libdirs="$cpl_cext_libdirs /usr/local/lib32"
                cpl_cext_libdirs="$cpl_cext_libdirs /usr/lib64"
                cpl_cext_libdirs="$cpl_cext_libdirs /usr/lib"
                cpl_cext_libdirs="$cpl_cext_libdirs /usr/lib32"

                test -n "$CPLDIR" && \
                    cpl_cext_libdirs="$CPLDIR/lib64 $CPLDIR/lib $CPLDIR/lib32 \
                                         $cpl_cext_libdirs"

            else

                cpl_cext_libdirs="$cpl_with_cext/lib64"
                cpl_cext_libdirs="$cpl_cext_libdirs $cpl_with_cext/lib"
                cpl_cext_libdirs="$cpl_cext_libdirs $cpl_with_cext/lib32"

            fi
            
        else
            cpl_cext_libdirs="$cpl_with_cext_libs"
        fi

        ESO_FIND_FILE($cpl_cext_check_lib, $cpl_cext_libdirs,
                      cpl_cext_libraries)


        if test x"$cpl_cext_includes" = xno || \
            test x"$cpl_cext_libraries" = xno; then
            cpl_cext_notfound=""

            if test x"$cpl_cext_includes" = xno; then
                if test x"$cpl_cext_libraries" = xno; then
                    cpl_cext_notfound="(headers and libraries)"
                else
                    cpl_cext_notfound="(headers)"
                fi
            else
                cpl_cext_notfound="(libraries)"
            fi

            AC_MSG_ERROR([libcext $cpl_cext_notfound was not found on your system. Please check!])
        else
            AC_MSG_RESULT([libraries $cpl_cext_libraries, headers $cpl_cext_includes])
        fi


        # Set up the symbols

        CX_INCLUDES="-I$cpl_cext_includes"
        CX_LDFLAGS="-L$cpl_cext_libraries"
        LIBCEXT="-lcext"
        
        
        AC_MSG_CHECKING([whether libcext can be used])
        AC_LANG_PUSH(C)
        
        cpl_cext_cflags_save="$CFLAGS"
        cpl_cext_ldflags_save="$LDFLAGS"
        cpl_cext_libs_save="$LIBS"

        CFLAGS="$CX_INCLUDES"
        LDFLAGS="$CX_LDFLAGS"
        LIBS="$LIBCEXT"
        
        AC_LINK_IFELSE([AC_LANG_PROGRAM(
                       [[
                       #include <cxutils.h>
                       ]],
                       [
                       cx_program_set_name("MyProgram");
                       ])],
                       [cpl_cext_is_usable="yes"],
                       [cpl_cext_is_usable="no"])

        AC_MSG_RESULT([$cpl_cext_is_usable])
        
        AC_LANG_POP(C)
        
        CFLAGS="$cpl_cext_cflags_save"
        LDFLAGS="$cpl_cext_ldflags_save"
        LIBS="$cpl_cext_libs_save"

        if test x"$cpl_cext_is_usable" = xno; then
            AC_MSG_ERROR([Linking with libcext failed! Please check architecture!])
        fi
        
    else
    
        AC_MSG_RESULT([disabled])
        AC_MSG_WARN([libcext checks have been disabled! This package may not build!])
        CX_INCLUDES=""
        CX_LDFLAGS=""
        LIBCEXT=""
        
    fi

    AC_SUBST(CX_INCLUDES)
    AC_SUBST(CX_LDFLAGS)
    AC_SUBST(LIBCEXT)

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

    # Check for the wcs includes
    if test -z "$cpl_with_wcs_includes"; then
        test -n "$WCSDIR" && cpl_wcs_incdirs="$WCSDIR/include"
    else
        cpl_wcs_incdirs="$cpl_with_wcs_includes"
    fi
    ESO_FIND_FILE($cpl_wcs_check_header, $cpl_wcs_incdirs, cpl_wcs_includes)

    # Check for the wcs library
    if test -z "$cpl_with_wcs_libs"; then
        test -n "$WCSDIR" && cpl_wcs_libdirs="$WCSDIR/lib"
    else
        cpl_wcs_libdirs="$cpl_with_wcs_libs"
    fi
    ESO_FIND_FILE($cpl_wcs_check_lib, $cpl_wcs_libdirs, cpl_wcs_libraries)

    if test x"$cpl_wcs_includes" = xno || test x"$cpl_wcs_libraries" = xno; then
        AC_MSG_WARN([wcs was not found on your system.])
    else
        AC_MSG_RESULT([libraries $cpl_wcs_libraries, headers $cpl_wcs_includes])
        # Attempt to check the version by checking the include files
        cpl_wcs_check_vers43=`grep "WCSLIB 4.3 - an implementation of the FITS WCS standard" $cpl_wcs_includes/wcslib/wcslib.h`
        if test -z "$cpl_wcs_check_vers43" ; then
            cpl_wcs_check_vers44=`grep "WCSLIB 4.4 - an implementation of the FITS WCS standard" $cpl_wcs_includes/wcslib/wcslib.h`
            if test -z "$cpl_wcs_check_vers44" ; then
                AC_MSG_WARN([wcs version seems to be older than 4.3])
            fi
        fi
        AC_DEFINE_UNQUOTED(CPL_WCS_INSTALLED, 1, [Defined if WCS is available])
        # Set up the symbols
        WCS_INCLUDES="-I$cpl_wcs_includes/wcslib"
        WCS_LDFLAGS="-L$cpl_wcs_libraries"
        LIBWCS="-lwcs"

        AC_SUBST(WCS_INCLUDES)
        AC_SUBST(WCS_LDFLAGS)
        AC_SUBST(LIBWCS)
    fi

])


# CPL_CHECK_FFTW
#---------------
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

    # Check for the fftw includes
    if test -z "$cpl_with_fftw_includes"; then
        test -n "$FFTWDIR" && cpl_fftw_incdirs="$FFTWDIR/include"
    else
        cpl_fftw_incdirs="$cpl_with_fftw_includes"
    fi
    ESO_FIND_FILE($cpl_fftw_check_header, $cpl_fftw_incdirs, cpl_fftw_includes)
    ESO_FIND_FILE($cpl_fftwf_check_header, $cpl_fftw_incdirs, cpl_fftwf_includes)

    # Check for the fftw library
    if test -z "$cpl_with_fftw_libs"; then
        test -n "$FFTWDIR" && cpl_fftw_libdirs="$FFTWDIR/lib"
    else
        cpl_fftw_libdirs="$cpl_with_fftw_libs"
    fi
    ESO_FIND_FILE($cpl_fftw_check_lib, $cpl_fftw_libdirs, cpl_fftw_libraries)
    ESO_FIND_FILE($cpl_fftwf_check_lib, $cpl_fftw_libdirs, cpl_fftwf_libraries)

    if test x"$cpl_fftw_includes" = xno || test x"$cpl_fftw_libraries" = xno; then
        AC_MSG_WARN([fftw (normal-precision) was not found on your system.])
    else
        AC_MSG_RESULT([libraries $cpl_fftw_libraries, headers $cpl_fftw_includes])
        # FIXME: Attempt to check the version

        AC_DEFINE_UNQUOTED(CPL_FFTW_INSTALLED, 1, [Defined if FFTW (normal-precision) is available])
        # Set up the symbols
        FFTW_INCLUDES="-I$cpl_fftw_includes"
        FFTW_LDFLAGS="-L$cpl_fftw_libraries"
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
        FFTWF_INCLUDES="-I$cpl_fftwf_includes"
        FFTWF_LDFLAGS="-L$cpl_fftwf_libraries"
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
    AC_REQUIRE([CPL_CHECK_CEXT])
    
    AC_MSG_CHECKING([for CPL])

    cpl_check_cpl_header="cpl.h"
    cpl_check_cpl_lib="libcplcore.a"

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
        
            if test -z "$cpl_with_cpl"; then
            
                # Try some known system locations
                
                cpl_incdirs="/opt/cpl/include"
                cpl_incdirs="$cpl_incdirs /usr/local/include"
                cpl_incdirs="$cpl_incdirs /usr/include"

                test -n "$CPLDIR" && \
                    cpl_incdirs="$CPLDIR/include \
                                 $cpl_incdirs"

            else

                cpl_incdirs="$cpl_with_cpl/include"

            fi
            
        else
            cpl_incdirs="$cpl_with_cpl_includes"
        fi

        ESO_FIND_FILE($cpl_check_cpl_header, $cpl_incdirs, cpl_includes)


        # Check for the CPL libraries

        if test -z "$cpl_with_cpl_libs"; then

            if test -z "$cpl_with_cpl"; then
            
                # Try some known system locations

                cpl_libdirs="/opt/cpl/lib"
                cpl_libdirs="$cpl_libdirs /usr/local/lib64"
                cpl_libdirs="$cpl_libdirs /usr/local/lib"
                cpl_libdirs="$cpl_libdirs /usr/local/lib32"
                cpl_libdirs="$cpl_libdirs /usr/lib64"
                cpl_libdirs="$cpl_libdirs /usr/lib"
                cpl_libdirs="$cpl_libdirs /usr/lib32"

                test -n "$CPLDIR" && \
                    cpl_libdirs="$CPLDIR/lib64 $CPLDIR/lib $CPLDIR/lib32 \
                                 $cpl_libdirs"

            else

                cpl_libdirs="$cpl_with_cpl/lib64"
                cpl_libdirs="$cpl_libdirs $cpl_with_cpl/lib"
                cpl_libdirs="$cpl_libdirs $cpl_with_cpl/lib32"

            fi
            
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

        CPL_INCLUDES="-I$cpl_includes $CX_INCLUDES $CFITSIO_INCLUDES"
        CPL_LDFLAGS="-L$cpl_libraries $CX_LDFLAGS $CFITSIO_LDFLAGS"
        CPL_CREATE_SYMBOLS
 
 
        AC_MSG_CHECKING([whether CPL can be used])
        AC_LANG_PUSH(C)
        
        cpl_cflags_save="$CFLAGS"
        cpl_ldflags_save="$LDFLAGS"
        cpl_libs_save="$LIBS"

        CFLAGS="$CPL_INCLUDES"
        LDFLAGS="$CPL_LDFLAGS"
        LIBS="$LIBCPLCORE"
        
        AC_LINK_IFELSE([AC_LANG_PROGRAM(
                       [[
                       #include <cpl.h>
                       ]],
                       [
                       cpl_init(CPL_INIT_DEFAULT);
                       ])],
                       [cpl_is_usable="yes"],
                       [cpl_is_usable="no"])

        AC_MSG_RESULT([$cpl_is_usable])
        
        AC_LANG_POP(C)
        
        CFLAGS="$cpl_cflags_save"
        LDFLAGS="$cpl_ldflags_save"
        LIBS="$cpl_libs_save"

        if test x"$cpl_is_usable" = xno; then
            AC_MSG_ERROR([Linking with CPL failed! Please check architecture!])
        fi
        
    else
    
        AC_MSG_RESULT([disabled])
        AC_MSG_WARN([CPL checks have been disabled! This package may not build!])
        CPL_INCLUDES=""
        CPL_LDFLAGS=""
        LIBCPLCORE=""
        LIBCPLDRS=""
        LIBCPLUI=""
        LIBCPLDFS=""
        
    fi

    AC_SUBST(CPL_INCLUDES)
    AC_SUBST(CPL_LDFLAGS)
    AC_SUBST(LIBCPLCORE)
    AC_SUBST(LIBCPLDRS)
    AC_SUBST(LIBCPLUI)
    AC_SUBST(LIBCPLDFS)

])
