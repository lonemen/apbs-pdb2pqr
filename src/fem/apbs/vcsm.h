/* ///////////////////////////////////////////////////////////////////////////
/// MC = < Manifold Code >
///
/// Copyright (C) 1993  Michael Holst
/// Copyright (C) 1999  Contributing authors listed in the code documentation
///                     retain the copyrights to their code contributions.
///
/// The program MC is copyrighted software, and there are restrictions on its
/// use, modification, and distribution; please refer to the document COPYING
/// which accompanies this software.
///
/// This program is distributed in the hope that it will be useful,
/// but WITHOUT ANY WARRANTY; without even the implied warranty of
/// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
/// See the document COPYING for more details.
///
/// You should have received a copy of the COPYING file with this program;
/// if not, write to the author Michael Holst at:  mholst@math.ucsd.edu
///
/// rcsid="$Id$"
/// /////////////////////////////////////////////////////////////////////// */

/* ///////////////////////////////////////////////////////////////////////////
// File:     vcsm.h    < vcsm.c >
//
// Purpose:  
//    Class Vcsm:  
//      A charge-simplex map for evaluating integrals of delta functions
//      with a Lagrange finite element basis.
//
// Author:   Nathan Baker
/////////////////////////////////////////////////////////////////////////// */

#ifndef _VCSM_H_
#define _VCSM_H_

#include "mc/vhal.h"
#include "mc/vgm.h"
#include "mc/vram.h"
#include "mc/ves.h"


#include "mc/vatom.h"
#include "mc/valist.h"
#include "mc/vlink.h"
#include "mc/vpool.h"

/* ///////////////////////////////////////////////////////////////////////////
// Class Vcsm: Parameters and datatypes
/////////////////////////////////////////////////////////////////////////// */

/* ///////////////////////////////////////////////////////////////////////////
// Class Vcsm: Definition
/////////////////////////////////////////////////////////////////////////// */

typedef struct Vcsm { 

  Valist *alist;      /* Atom (charge) list */
  int natom;          /* Size of thee->alist; redundant, but useful for
                       * convenience */
  Vpool *pool;        /* A pool of Vlink objects */
  Vgm *gm;            /* Grid manager (container class for master vertex
                       * and simplex lists as well as prolongation
                       * operator for updating after refinement ) */
  Vlink **sqm;        /* The map which gives the list charges associated with
                       * each simplex in gm->simplices.  The indices of
                       * the first dimension are associated with the
                       * simplex ID's in Vgm.  This is an array of pointers
                       * to the first items in linked lists of charges
                       * (Vlink objects) */
  int nsimp;          /* The _currently used) length of sqm, nsqm -- may not 
                       * always be up-to-date with Vgm */
  int msimp;          /* The maximum number of entries that can be 
                       * accomodated by sqm or nsqm  -- saves on realloc's */
  int initFlag;       /* Indicates whether the maps have been initialized
                       * yet */

} Vcsm;

/* ///////////////////////////////////////////////////////////////////////////
// Class Vcsm: Inlineable methods (vcsm.c)
/////////////////////////////////////////////////////////////////////////// */

#if !defined(VINLINE_VCSM)
#else /* if defined(VINLINE_VCSM) */
#endif /* if !defined(VINLINE_VCSM) */

/* ///////////////////////////////////////////////////////////////////////////
// Class Vcsm: Non-Inlineable methods (vcsm.c)
/////////////////////////////////////////////////////////////////////////// */

VEXTERNC Vcsm*   Vcsm_ctor(Valist *alist, Vgm *gm);
VEXTERNC int     Vcsm_ctor2(Vcsm *thee, Valist *alist, Vgm *gm);
VEXTERNC void    Vcsm_dtor(Vcsm **thee);
VEXTERNC void    Vcsm_dtor2(Vcsm *thee);

VEXTERNC Valist* Vcsm_getValist(Vcsm *thee);
VEXTERNC Vgm*    Vcsm_getVgm(Vcsm *thee);
VEXTERNC int     Vcsm_getNumberAtoms(Vcsm *thee, int isimp);
VEXTERNC Vatom*  Vcsm_getAtom(Vcsm *thee, int iatom, int isimp);

VEXTERNC void    Vcsm_init(Vcsm *thee);
VEXTERNC int     Vcsm_update(Vcsm *thee, SS **simps, int num);

#endif /* ifndef _VALIST_H_ */
