# -*- coding: utf-8 -*-

###CONVERSION OF PHILIPS DATA (CLASSIC DICOM)###


"""
Created on Wed Aug 09 11:50:03 2017

@author: plally
"""

import dicom
#import Tkinter, tkFileDialog
import os, os.path
from dicom.filereader import InvalidDicomError
import glob
import struct
import array
import copy
import numpy as np


def process_mrs_philips_dicom_cl(dcm_dir):    
#    # Make a top-level instance and hide in top left corner, get filepath
#    root = Tkinter.Tk()
#    root.geometry('0x0+0+0')
#    root.attributes("-topmost", 1)
#    dcm_dir = tkFileDialog.askdirectory(parent=root)
#    root.attributes("-topmost", 0)
#    root.destroy()
#    
    root_dir=os.path.abspath(os.path.join(dcm_dir, os.pardir))
    pat_name=os.path.split(os.path.dirname(dcm_dir))[1]
    
    f = file(root_dir + '/preproc_dump.txt', 'w')
    
    l=[]
    for fname in ( glob.glob(dcm_dir + '/*/XX*') + glob.glob(dcm_dir + '/XX*') ):
        try:
            d0 = dicom.read_file(fname)
            try:
                if [0x2005,0x1035] in d0:            
                    if d0[0x2005,0x1035].value == "SPECTRA":
                        l.append([fname,int(d0.SeriesNumber),d0[0x2005,0x1313].value,d0[0x2005,0x140f][0][0x0028,0x9002].value,d0[0x2005,0x140f][0][0x0028,0x9001].value])
            except AttributeError:
                continue
            except IOError:
                print 'no such file'
            except KeyError:
                continue
        except InvalidDicomError:
                print str(fname) + ': Invalid Dicom file'
        
    for nlist in range(0,len(l)):
        if l[nlist][2]==1:
            try:
                d = dicom.read_file(l[nlist][0])
                d.SpectroscopyAcquisitionDataColumns = d[0x2005,0x140f][0][0x0018,0x9127].value
                d.ProtocolName=str(d.ProtocolName).replace (" ","_")
                print >>f, 'file: '+l[nlist][0]+'\tSeries: '+d.ProtocolName
                #d.save_as(root_dir + '/' + pat_name + '_PREPROC_LCM/' + fname_new)            
                d.WaterReferencedPhaseCorrection = d[0x2005,0x140f][0][0x0018,0x9199].value
                if d[0x2005,0x140f][0][0x0018,0x9199].value =="YES":
                    ecc_str = 'ECC'               
                else:
                    ecc_str = 'NO_ECC'        
                fname_new=(str(d.SeriesNumber)+'_'+str(d.ProtocolName)+'_'+str(d[0x2001,0x1081].value)+'_'+ecc_str)
                series=l[nlist][1]
                npts=l[nlist][3]
                avg=0
                for plist in range(0,len(l)):
                    if l[plist][1]==series:
                        avg=avg+1
    #                print(avg)                 
                spec_data=[]
                spec_data[0:(npts*2)]=array.array('f',struct.unpack(str(npts*2)+'f',d[0x2005,0x1270].value))
                for plist in range(0,len(l)):
                    if l[plist][1]==series:
    #                        print(l[plist][0])
                        d_sub = dicom.read_file(l[plist][0])
                        d_sub.ProtocolName=str(d_sub.ProtocolName).replace(" ","_")
                        nsub=int(l[plist][2]-1)
                        spec_data[(nsub*npts*2):((nsub+1)*npts*2)]=array.array('f',struct.unpack(str(npts*2)+'f',d_sub[0x2005,0x1270].value))
                        print >>f, 'file: '+l[plist][0]+'\tSeries: '+d_sub.ProtocolName
    #                        print(l[plist][0])
                d.SpectroscopyData=[]
                d.SpectroscopyData=list(spec_data)
                d.SpectralWidth=d[0x2005,0x1357].value
                d.EffectiveEchoTime=d[0x2001,0x1025].value
                d.EffectiveEchoTime=float(d.EffectiveEchoTime)
                d.EchoTime=d.EffectiveEchoTime
                if np.size(d[0x2005,0x1030].value) > 1:
                    d.RepetitionTime=d[0x2005,0x1030][0]
                else:
                    d.RepetitionTime=d[0x2005,0x1030].value 
                
                seqtype=d[0x2005,0x140f][0][0x0018,0x9054][:]

                
                if seqtype == 'PRIME':
                    d.VolumeLocalizationTechnique = 'PRESS'
                elif seqtype == 'STEAM':
                    d.VolumeLocalizationTechnique = 'STEAM'
                d.SOPInstanceUID = dicom.UID.generate_uid()
                d.TransmitterFrequency=d[0x2001,0x1083].value
                if not os.path.exists(root_dir + '/' + pat_name + '_PREPROC_LCM'):
                    os.makedirs(root_dir + '/' + pat_name + '_PREPROC_LCM')
#                if not os.path.exists(root_dir + '/' + pat_name + '_LCM_Results'):
#                    os.makedirs(root_dir + '/' + pat_name + '_LCM_Results')

                if d.WaterReferencedPhaseCorrection =="YES":

                    fname_new_water=fname_new+'_WATER'
                    d_w=copy.deepcopy(d)
                    d_ws=copy.deepcopy(d)
                    d_w.SOPInstanceUID = dicom.UID.generate_uid()
                    d_ws.SOPInstanceUID = dicom.UID.generate_uid()
                    d_w.SpectroscopyData=[]
                    d_ws.SpectroscopyData=[]                    
                    d_w.SpectroscopyData=list(spec_data[len(spec_data)/2:])
                    d_ws.SpectroscopyData=list(spec_data[0:len(spec_data)/2])
                    d_w.save_as(os.path.join(root_dir,pat_name + '_PREPROC_LCM',fname_new_water))
                    d_ws.save_as(os.path.join(root_dir,pat_name + '_PREPROC_LCM',fname_new))
                else:      
#                    fname_new=(str(d.SeriesNumber)+'_'+str(d.ProtocolName)+'_'+str(int(d[0x2001,0x1081].value))+'_'+ecc_str)
                    d.save_as(os.path.join(root_dir,pat_name + '_PREPROC_LCM',fname_new))


#                d.save_as(root_dir + '/' + pat_name + '_PREPROC_LCM/' + fname_new)            
            except AttributeError:
                print('...')
            except IOError:
                print 'no such file'
            except InvalidDicomError:
                print 'Invalid Dicom file'
    
    
    f.close()
    print('DONE!')                