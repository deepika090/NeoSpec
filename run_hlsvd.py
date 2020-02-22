# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 09:47:51 2015

Function to handle HLSVD processing with given parameters

@author: plally
"""

# Python modules
from __future__ import division


# 3rd party modules
import numpy as np

# Vespa modules
import hlsvdpro as hlsvd

np.set_printoptions(precision=15)

def hlsvdfilt(mrs_data,nc,vals):
    print(vals)
    sig_cx=mrs_data.raw_cx
    #create new window-----------
    fit=np.zeros_like(sig_cx)
    
    for n in vals:
        observed = sig_cx[n][0:mrs_data.pts_orig]
        step_size = 1000/mrs_data.bw
        
        # Call hlsvd()
        results = hlsvd.hlsvd(observed, nc, step_size)
        
        
        nsv_found, singular_values, frequencies, \
            damping_factors, amplitudes, phases = results
        
        estimated = _create_hlsvd_sum_fid(frequencies, damping_factors, 
                                          amplitudes, phases, 
                                          len(observed), step_size)
        
        # We're only concerned with the real portion of the data
        sig_cx[n][0:mrs_data.pts_orig]=observed-estimated    
        fit[n][0:mrs_data.pts_orig]=estimated             
       
        # The observed values are always noisier, so plotting them first allows
        # the cleaner estimation to be displayed on top. 
    
    return(sig_cx,fit)




def hlsvdquant(mrs_data,nc,vals):    
    print(vals)
#    sig_cx=np.real(mrs_data.raw_cx)+1j*np.imag(mrs_data.raw_cx)

    sig_cx=np.abs(mrs_data.raw_cx)+0j
    #create new window-----------
    fit=np.zeros_like(sig_cx)
    h2o_amp=np.zeros(shape=mrs_data.nsa)+0j
    for n in vals:
        nc0=nc        
        observed = sig_cx[n][2:mrs_data.pts_orig]
        step_size = 1000/mrs_data.bw

        while nc0>0:
            # Call hlsvd()
            results = hlsvd.hlsvd(observed, nc0, step_size)
            
            
            nsv_found, singular_values, frequencies, \
                damping_factors, amplitudes, phases = results
            
            if max(damping_factors)>-7.96:
                nc0=nc0-1                
                continue
            else:
                estimated = _create_hlsvd_sum_fid(frequencies, damping_factors, 
                                                   amplitudes, phases, 
                                                   len(observed), step_size)
                # We're only concerned with the real portion of the data
                sig_cx[n][2:mrs_data.pts_orig]=observed-estimated    
                fit[n][2:mrs_data.pts_orig]=estimated
#                print('SPEC ['+str(n)+']: '+str(nc0)+' COMPONENTS, '+str(abs(fit[n][3])))
                print(str(abs(fit[n][3])))
                h2o_amp[n]=fit[n][3]
                break
            
            
           
        # The observed values are always noisier, so plotting them first allows
        # the cleaner estimation to be displayed on top. 
        
    
    
    return(h2o_amp,fit)


# swiped from functors/funct_hlsvd_create_fids.py, modified for this code
def _create_hlsvd_sum_fid(frequencies, decays, areas, phases, 
                           ndata_points, dwell_time):

    """ 
    Construct time domain signal from the estimated parameters.
    
    """
    result = np.zeros((len(frequencies), ndata_points), dtype=complex)
    t = np.arange(ndata_points) * dwell_time 
    
    K = 1j * 2 * np.pi
    # K is an invariant for the loop below

    for i, decay in enumerate(decays):
        if (decays[i]<-0) and (abs(frequencies[i]) < 0.05112):
            # PL ADDED - ONLY CHOOSE LINEWIDTHS < 0 and FREQS 0.4ppm FROM CENTRE
            # We frequently force the exp() function here into very small 
            # values that raise the following exception:
            #    FloatingPointError: underflow encountered in exp
            # Handling those exceptions with try/except is not an option 
            # because raising the exception interrupts the calculation.
            # Instead, we temporarily disable numpy's error reporting,
            # allow it to silently generate NaNs, and then change those NaNs
            # to 0.0.
            old_settings = np.seterr(all='ignore')
            
            line_result = areas[i] * np.exp((t/decays[i]) + \
                          K * (frequencies[i]*t+phases[i]/360.0))
            
            zeros = np.zeros_like(line_result)

            result[i,:] = np.where(np.isnan(line_result), zeros, line_result)
            np.seterr(**old_settings)

        else:
            result[i,:] = result[i,:] * 0
    return np.sum(result, axis=0)

