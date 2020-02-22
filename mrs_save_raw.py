# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 18:16:18 2015

@author: plally
"""
import os
import numpy

def mrs2raw(mrs_data,raw_dir,prefix):
    for avg in mrs_data.vals: 
        f = file(os.path.join(raw_dir,prefix+'_'+str(avg)+'.RAW'), 'wb')
        f.write(' $DUMMY\n')
        f.write(' DELTAT=' + str(1/mrs_data.bw) + '\n')
        f.write(' BW=' + str(mrs_data.bw) + '\n')
        f.write(' $END\n\n')
        f.write(' $SEQPAR\n')
        f.write(' ECHOT=' + str(mrs_data.te)+ '\n')
        f.write(' HZPPPM='+ str(mrs_data.f0)+'\n')
        f.write(' NUNFIL='+ str(mrs_data.pts_orig)+'\n')            
        f.write(' SEQ='"'"+ str(mrs_data.seqtype)+"'\n")
        f.write(' $END\n\n')
        f.write(' $NMID\n')
        f.write(' ID='"'" + os.path.split(raw_dir)[1] + "'\n")
        f.write(' FMTDAT='"'(2E15.6)'"'\n')
        f.write(' VOLUME=1.0\n' )
        f.write(' TRAMP=1.0\n' )
        f.write(' BRUKER=T\n')
        f.write(' $END\n\n')
        for pt in range(0,mrs_data.pts_orig):
            f.write( '%15.6E%15.6E\n' %(numpy.real(mrs_data.raw_cx[avg,pt]),numpy.imag(mrs_data.raw_cx[avg,pt])))

        f.close()
    
def mrs2raw_phantom(mrs_data,raw_dir,prefix):
    zf_buffer=4
    apod=5.0
    for avg in mrs_data.vals: 
        f = file(os.path.join(raw_dir,prefix+'_'+str(avg)+'.RAW'), 'wb')
        f.write(' $DUMMY\n')
        f.write(' DELTAT=' + str(1/mrs_data.bw) + '\n')
        f.write(' ***THIS IS A PHANTOM: BROADENED AND ZEROFILLED*** \n')
        f.write(' BW=' + str(mrs_data.bw) + '\n')
        f.write(' $END\n\n')
        f.write(' $SEQPAR\n')
        f.write(' ECHOT=' + str(mrs_data.te)+ '\n')
        f.write(' HZPPPM='+ str(mrs_data.f0)+'\n')
        f.write(' NUNFIL='+ str(mrs_data.pts_orig*zf_buffer)+'\n')            
        f.write(' SEQ='"'PRESS'"'\n' )
        f.write(' $END\n\n')
        f.write(' $NMID\n')
        f.write(' ID='"'" + os.path.split(raw_dir)[1] + "'\n")
        f.write(' FMTDAT='"'(2E15.6)'"'\n')
        f.write(' VOLUME=1.0\n' )
        f.write(' TRAMP=1.0\n' )
        f.write(' BRUKER=T\n')
        f.write(' $END\n\n')
        for pt in range(0,mrs_data.pts_orig):
            f.write( '%15.6E%15.6E\n' %(numpy.real(mrs_data.raw_cx[avg,pt]*numpy.exp(-apod*mrs_data.fscale[pt]/mrs_data.bw)),numpy.imag(mrs_data.raw_cx[avg,pt]*numpy.exp(-apod*mrs_data.fscale[pt]/mrs_data.bw))))
        for pt in range(0,mrs_data.pts_orig*(zf_buffer-1)):
            f.write( '%15.6E%15.6E\n' %(0.0,0.0))
        f.close()