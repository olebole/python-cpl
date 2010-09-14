## Process this file with automake to produce Makefile.in

##   This file is part of the IIINSTRUMENT Pipeline
##   Copyright (C) 2002,2003 European Southern Observatory

##   This library is free software; you can redistribute it and/or modify
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

DISTCLEANFILES = *~


if MAINTAINER_MODE

MAINTAINERCLEANFILES = Makefile.in

endif


INCLUDES = $(all_includes)

noinst_HEADERS = 

plugin_LTLIBRARIES = rrrecipe.la 

rrrecipe_la_SOURCES = rrrecipe.c 
rrrecipe_la_LIBADD = $(LIBIIINSTRUMENT)
rrrecipe_la_LDFLAGS = -module -avoid-version
rrrecipe_la_DEPENDENCIES = $(LIBIIINSTRUMENT)
