# -*- coding: utf-8 -*-
"""
Created on Wed Apr 08 18:14:29 2015

PERFORMS ZEROFILLING/TRUNCATION ON AN MRS DATA STRUCTURE

@author: plally
"""
import numpy
import copy

class TruncError(Exception): pass
    
def zerofill(mrs_data_orig,zff):
    mrs_data=copy.deepcopy(mrs_data_orig)
    if mrs_data.pts*zff >= mrs_data.pts_orig:
        mrs_data.pts=int(mrs_data.pts*zff)
        mrs_data.fscale=numpy.arange(0,mrs_data.pts,1)
        mrs_data.ppmscale=4.65+((mrs_data.fscale-mrs_data.fscale[-1]/2.0)*mrs_data.bw/(mrs_data.pts))/mrs_data.f0
        tgt=numpy.zeros((numpy.size(mrs_data.raw_cx,axis=0),int(zff*numpy.size(mrs_data.raw_cx,axis=1))),dtype=numpy.complex128)
        orig_sz=numpy.size(mrs_data.raw_cx,axis=1)
        tgt_sz=numpy.size(tgt,axis=1)
        
        lim=min(orig_sz,tgt_sz)
        tgt[:,0:lim]=mrs_data.raw_cx[:,0:lim]
        
        mrs_data.raw_cx=tgt
    
        mrs_data.zf=True
    else:
        mrs_data.zf=False
        raise TruncError, 'DENIED: Further truncation will cause raw data loss!'
    return(mrs_data)