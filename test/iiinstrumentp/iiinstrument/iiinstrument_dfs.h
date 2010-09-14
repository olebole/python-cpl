/* $Id: iiinstrument_dfs.h,v 1.9 2007/07/31 06:10:40 llundin Exp $
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
 * $Revision: 1.9 $
 * $Name:  $
 */

#ifndef IIINSTRUMENT_DFS_H
#define IIINSTRUMENT_DFS_H

/*-----------------------------------------------------------------------------
                                   Define
 -----------------------------------------------------------------------------*/

/* Define here the PRO.CATG keywords */
#define RRRECIPE_XXX_PROCATG            "THE_PRO_CATG_VALUE"

/* Define here the DO.CATG keywords */
#define RRRECIPE_RAW                    "RRRECIPE_DOCATG_RAW"
#define IIINSTRUMENT_CALIB_FLAT         "FLAT"

/*-----------------------------------------------------------------------------
                                Functions prototypes
 -----------------------------------------------------------------------------*/

cpl_error_code iiinstrument_dfs_set_groups(cpl_frameset *);

#endif
