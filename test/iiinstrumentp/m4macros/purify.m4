# PURIFY
#------------------------
# Checks for the INTROOT area
AC_DEFUN([CHECK_PURIFY],
[

    AC_MSG_CHECKING([for PURIFY availability])

    AC_ARG_ENABLE(purify,
      AC_HELP_STRING([--disable-purify],
        [disables the check for the PURIFY installation]),
        enable_purify=$enableval,
        enable_purify=yes)

    if test "x$enable_purify" = xyes ; then
      AC_CHECK_PROG([PURIFY_CMD], [purify], [purify],[NONE])
      if test "$PURIFY_CMD" = "NONE" ; then
        AC_MSG_RESULT([disabled])
        enable_purify=no
      else
        AC_MSG_RESULT([enabled])
      fi
    else
      AC_MSG_RESULT([disabled])
    fi

    AM_CONDITIONAL([PURIFY], [test "x$enable_purify" = "xyes"])
])
