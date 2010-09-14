/* $Id: iiinstrument_pfits.h,v 1.8 2007/07/31 06:10:40 llundin Exp $
 *
 * This file is part of the IIINSTRUMENT Pipeline
 * Copyright (C) 2002,2003 European Southern Observatory
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

/*
 * $Author: llundin $
 * $Date: 2007/07/31 06:10:40 $
 * $Revision: 1.8 $
 * $Name:  $
 */

#ifndef IIINSTRUMENT_PFITS_H
#define IIINSTRUMENT_PFITS_H

/*-----------------------------------------------------------------------------
                                   Includes
 -----------------------------------------------------------------------------*/

#include <cpl.h>

/*-----------------------------------------------------------------------------
                                   Functions prototypes
 -----------------------------------------------------------------------------*/

const char * iiinstrument_pfits_get_arcfile(const cpl_propertylist *) ;
double iiinstrument_pfits_get_dit(const cpl_propertylist *) ;

#endif
