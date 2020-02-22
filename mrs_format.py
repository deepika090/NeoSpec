# -*- coding: utf-8 -*-
"""
Created on Wed Apr 08 15:21:53 2015

DEFINES THE SPECTROSCOPY CLASS


@author: plally
"""

import numpy

class mrs_struct(object):
    def __init__(self, dcm):
        self.nsa=int(len(dcm.SpectroscopyData)/(dcm.SpectroscopyAcquisitionDataColumns*2)) # x2 since includes both re + im
        self.bw=dcm.SpectralWidth
        self.pts=dcm.SpectroscopyAcquisitionDataColumns
        self.pts_orig=dcm.SpectroscopyAcquisitionDataColumns
        self.f0=dcm.TransmitterFrequency
        self.te=dcm.EchoTime
        self.tr=dcm.RepetitionTime
        self.sig_im = numpy.zeros(shape=(self.nsa,self.pts))
        self.sig_re = numpy.zeros(shape=(self.nsa,self.pts))
        for avg in range(0,self.nsa):
            self.sig_re[avg,0:self.pts] = dcm.SpectroscopyData[(self.pts*2*avg)+0:(self.pts*2*avg)+self.pts*2:2]    
            self.sig_im[avg,0:self.pts] = dcm.SpectroscopyData[(self.pts*2*avg)+1:(self.pts*2*avg)+self.pts*2:2]
        self.raw_cx = self.sig_re + 1j * self.sig_im
        self.hlsvd=numpy.zeros(self.nsa)            #flag up if hlsvd performed
        self.fit=numpy.zeros_like(self.raw_cx)
        self.fscale=numpy.arange(0,self.pts,1)
        self.eddy=False                             #flag up if data is to be corrected
        self.zf=False                               #flag up if data has been zerofilled
        self.h2o_dir=''                             #empty string for eddy corr water file
        self.h2o_amp=numpy.zeros(self.nsa)          #hlsvd fits
        self.vals=[]                             #empty array for eddy corr water file
        self.ppmscale=4.65+((self.fscale-self.fscale[-1]/2.0)*self.bw/(self.pts))/self.f0
        self.dcm_dir=''                             #empty string for original dicom file
        self.seqtype=dcm.VolumeLocalizationTechnique
        self.phantom=False                          #flag up if data is to be saved broadened and zerofilled