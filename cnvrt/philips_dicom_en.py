# -*- coding: utf-8 -*-

###CONVERSION OF PHILIPS DATA (ENHANCED DICOM)###

import dicom
#import Tkinter, tkFileDialog
import os, os.path
from dicom.filereader import InvalidDicomError
import glob
import copy
import numpy as np

def process_mrs_philips_dicom_en(dcm_dir):    
#    # Make a top-level instance and hide in top left corner, get filepath
#    root = Tkinter.Tk()
#    root.geometry('0x0+0+0')
#    root.attributes("-topmost", 1)
#    dcm_dir = tkFileDialog.askdirectory(parent=root)
#    root.attributes("-topmost", 0)
#    root.destroy()

    # Look at parent folder - use this as patient name
    root_dir=os.path.abspath(os.path.join(dcm_dir, os.pardir))
    pat_name=os.path.split(os.path.dirname(dcm_dir))[1]

    # Create file in parent folder to give details of all converted files
    f = file(root_dir + '/preproc_dump.txt', 'w')

    # Check all files in the directory - NOT RECURSIVE, only 1 folder deep
    for fname in glob.glob(os.path.join(dcm_dir,'*')):
        try:
            d = dicom.read_file(fname)
            try:
                if "AcquisitionContrast" in d:
                    if d.AcquisitionContrast == "SPECTROSCOPY":
                        print >>f, 'file: '+fname+'\tSeries: '+str(d.ProtocolName).replace (" ","_")
                        print('Extracting MRS data from '+os.path.split(fname)[1])
                        if not os.path.exists(os.path.join(root_dir,pat_name + '_PREPROC_LCM')):
                            os.makedirs(os.path.join(root_dir,pat_name + '_PREPROC_LCM'))
#                        if not os.path.exists(os.path.join(root_dir,pat_name + '_LCM_Results')):
#                            os.makedirs(os.path.join(root_dir,pat_name + '_LCM_Results'))

                        if d.WaterReferencedPhaseCorrection =="YES":
                            ecc_str = 'ECC'
                            fname_new=(str(d.SeriesNumber)+'_'+str(d.ProtocolName).replace (" ","_")+'_'+str(d.NumberOfFrames/2)+'_'+ecc_str)
                            fname_new_water=fname_new+'_WATER'
                            d.EffectiveEchoTime=float(d[0x2001,0x1025].value)
                            d.EchoTime=d.EffectiveEchoTime
                            if np.size(d[0x2005,0x1030].value) > 1:
                                d.RepetitionTime=d[0x2005,0x1030][0]
                            else:
                                d.RepetitionTime=d[0x2005,0x1030].value    
                            d.SOPInstanceUID = dicom.UID.generate_uid()
                            d_w=copy.deepcopy(d)
                            d_ws=copy.deepcopy(d)
                            d_w.SpectroscopyData=d.SpectroscopyData[len(d.SpectroscopyData)/2:]
                            d_ws.SpectroscopyData=d.SpectroscopyData[0:len(d.SpectroscopyData)/2]
                            d_w.save_as(os.path.join(root_dir,pat_name + '_PREPROC_LCM',fname_new_water))
                            d_ws.save_as(os.path.join(root_dir,pat_name + '_PREPROC_LCM',fname_new))                            
                        else:
                            ecc_str = 'NO_ECC'        
                            fname_new=(str(d.SeriesNumber)+'_'+str(d.ProtocolName).replace (" ","_")+'_'+str(d.NumberOfFrames)+'_'+ecc_str)
                            d.EffectiveEchoTime=float(d[0x2001,0x1025].value)
                            d.EchoTime=d.EffectiveEchoTime
                            if np.size(d[0x2005,0x1030].value) > 1:
                                d.RepetitionTime=d[0x2005,0x1030][0]
                            else:
                                d.RepetitionTime=d[0x2005,0x1030].value 
                            d.SOPInstanceUID = dicom.UID.generate_uid()
                            d.save_as(os.path.join(root_dir,pat_name + '_PREPROC_LCM',fname_new))
                    else:
                        print('Skipping '+os.path.split(fname)[1]+' - no MRS......')
                else:
                    print('Skipping '+os.path.split(fname)[1]+' - no MRS......')
            except AttributeError:
                print('...')
            except IOError:
                print 'no such file'
        except InvalidDicomError:
            print 'Invalid Dicom file'
    
    f.close()
    print('DONE!')