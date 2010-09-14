/* $Id: iiinstrument_pfits.c,v 1.12 2007/07/31 06:10:40 llundin Exp $
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
 * $Revision: 1.12 $
 * $Name:  $
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

/*-----------------------------------------------------------------------------
                                   Includes
 -----------------------------------------------------------------------------*/

#include <cpl.h>

#include "iiinstrument_pfits.h"

/*----------------------------------------------------------------------------*/
/**
 * @defgroup iiinstrument_pfits     FITS header protected access
 *
 */
/*----------------------------------------------------------------------------*/

/**@{*/

/*-----------------------------------------------------------------------------
                              Function codes
 -----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------*/
/**
  @brief    find out the arcfile   
  @param    plist       property list to read from
  @return   pointer to statically allocated character string
 */
/*----------------------------------------------------------------------------*/
const char * iiinstrument_pfits_get_arcfile(const cpl_propertylist * plist)
{
    const char * value = cpl_propertylist_get_string(plist, "ARCFILE");

    cpl_ensure(value != NULL, cpl_error_get_code(), NULL);

    return value;
}

/*----------------------------------------------------------------------------*/
/**
  @brief    find out the DIT value 
  @param    plist       property list to read from
  @return   the requested value
 */
/*----------------------------------------------------------------------------*/
double iiinstrument_pfits_get_dit(const cpl_propertylist * plist)
{
    cpl_errorstate prestate = cpl_errorstate_get();
    const double value = cpl_propertylist_get_double(plist, "ESO DET DIT");

    /* Check for a change in the CPL error state */
    /* - if it did change then propagate the error and return */
    cpl_ensure(cpl_errorstate_is_equal(prestate), cpl_error_get_code(), 0.0);

    return value;
}

/**@}*/
