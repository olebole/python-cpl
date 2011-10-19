## Process this file with automake to produce Makefile.in

##   This file is part of the iiinstrument Pipeline
##   Copyright (C) 2002,2003 European Southern Observatory

##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2 of the License, or
##   (at your option) any later version.

##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.

##   You should have received a copy of the GNU General Public License
##   along with this program; if not, write to the Free Software
##   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

AUTOMAKE_OPTIONS = 1.8 foreign

ACLOCAL_AMFLAGS = -I m4macros

DISTCLEANFILES = *~


COMPILE_FIRST = 

TOPSUBDIRS = iiinstrument recipes

COMPILE_LAST =


HTML_SUBDIRS =

SUBDIRS = $(COMPILE_FIRST) $(TOPSUBDIRS) $(COMPILE_LAST)

EXTRA_DIST = m4macros/eso.m4 m4macros/cpl.m4 admin/html.am \
	doxygen/Doxyfile.in setup 


pkgdata_DATA = ChangeLog AUTHORS NEWS README TODO


if MAINTAINER_MODE

DISTCHECK_CONFIGURE_FLAGS = --enable-maintainer-mode

MAINTAINERCLEANFILES = Makefile.in aclocal.m4 config.h.in configure stamp-h.in

clean-local: clean-html

dist-hook: html
	@if test -d $(top_srcdir)/html; then \
	  echo "cp -pr $(top_srcdir)/html $(distdir)"; \
	  cp -pr $(top_srcdir)/html $(distdir); \
	fi
	find $(distdir) -type d ! -perm -222 -exec chmod u+w {} \; -o \
	-type f ! -perm -222 -exec chmod u+w {} \; || chmod -R u+w $(distdir)

else

clean-local:

endif

uninstall-local: uninstall-html

libtool: $(LIBTOOL_DEPS)
	$(SHELL) ./config.status --recheck

