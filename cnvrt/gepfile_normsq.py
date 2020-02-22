# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 13:29:41 2018

@author: plall
"""

import dicom
#import Tkinter, tkFileDialog
import os, os.path
from dicom.dataset import Dataset, FileDataset
import struct
import glob
import time
import datetime
import numpy as np
import cmath

def process_mrs_ge(pfile_dir):    
    
    #         Make a top-level instance and hide in top left corner, get filepath
#    root = Tkinter.Tk()
#    root.geometry('0x0+0+0')
#    root.attributes("-topmost", 1)
#    pfile_dir = tkFileDialog.askdirectory(parent=root)
#    root.attributes("-topmost", 0)
#    root.destroy()
    print('Working...')
    root_dir=os.path.abspath(os.path.join(pfile_dir, os.pardir))
    pat_name=os.path.split(os.path.dirname(pfile_dir))[1]
    
    filelist=glob.glob(pfile_dir + '/*.7' )
    filelist.extend(glob.glob(pfile_dir + '/*.anon' ))
    for fname in filelist:
        try:
            print('')
            print(fname)
            fbin=open(fname,'rb')
            sw_ver=int(str(struct.unpack('f',fbin.read(4))[0]).split('.')[0])
            print('software version: ' + str(sw_ver))
            
            s=fbin.read()
            if s.find('PROBE-P') > 0:
                seqtype = 'PRESS'
            elif s.find('PROBE-S') >0:
                seqtype = 'STEAM'
            else:
                print('WARNING: acquisition type not recognised!')    
            
            if sw_ver < 26:
                fbin.seek(82)
                pt_sz=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(1468)
                hdr_sz=struct.unpack('<i',fbin.read(4))[0] 


                if sw_ver == 15:
                    fbin.seek(144580)   # FOR REV 15
                elif sw_ver == 16:
                    fbin.seek(144628)   # FOR REV 16
                elif sw_ver > 19:
                    fbin.seek(148404)   # FOR REV 20 & 24    
                te=struct.unpack('<i',fbin.read(4))[0]
        
                if sw_ver == 15:
                    fbin.seek(144572)   # FOR REV 15            
                elif sw_ver == 16:            
                    fbin.seek(144620)   # FOR REV 16
                elif sw_ver > 19 and sw_ver < 26:
                    fbin.seek(148396)   # FOR REV 20 & 24
                tr=struct.unpack('<i',fbin.read(4))[0]
                
                fbin.seek(148712)
                exam_no=struct.unpack('<i',fbin.read(4))[0]
                fbin.seek(148724)
                series_no=struct.unpack('<i',fbin.read(4))[0]
                fbin.seek(424)
                c_freq=struct.unpack('<i',fbin.read(4))[0]
                fbin.seek(200)
                st_rcv=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(202)
                en_rcv=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(70)
                nechoes=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(72)
                navs=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(74)
                nframes=struct.unpack('<h',fbin.read(2))[0]
                n_rcv=(en_rcv-st_rcv)+1
        #            pfile=headers.Pfile.from_file(fname)
        #            frm_sz=pfile.acq_x_res*2*pt_sz
        #            echo_size=frm_sz*pfile.acq_y_Res
        #            slice_size=echo_size*nechoes
        #            data_sz=pfile.acq_x_res*2*(pfile.acq_y_Res-1)
                fbin.seek(102)        
                acq_x_res=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(104)
                acq_y_Res=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(216)
                bandwidth=struct.unpack('<f',fbin.read(4))[0]
                
#                if sw_ver == 15:
#                    fbin.seek(948)   # FOR REV 15
#                elif sw_ver == 16:
#                    fbin.seek(948)   # FOR REV 16
#                elif sw_ver > 19:
#                    fbin.seek(948)   # FOR REV 20 & 24    
                fbin.seek(232)
                ws_nsa=struct.unpack('<f',fbin.read(4))[0]
                

                
            elif sw_ver == 26:
                fbin.seek(158)
                pt_sz=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(4)
                hdr_sz=struct.unpack('<i',fbin.read(4))[0]
                
                fbin.seek(199244)   # FOR REV 26    
                te=struct.unpack('<i',fbin.read(4))[0]
        
                fbin.seek(199236)   # FOR REV 26
                tr=struct.unpack('<i',fbin.read(4))[0]
                
                fbin.seek(196428)
                exam_no=struct.unpack('<i',fbin.read(4))[0]
                fbin.seek(194068)
                series_no=struct.unpack('<i',fbin.read(4))[0]
                fbin.seek(504)
                c_freq=struct.unpack('<i',fbin.read(4))[0]
                fbin.seek(264)
                st_rcv=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(266)
                en_rcv=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(146)
                nechoes=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(148)
                navs=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(2520)
                nframes=struct.unpack('<h',fbin.read(2))[0]
                n_rcv=(en_rcv-st_rcv)+1
        #            pfile=headers.Pfile.from_file(fname)
        #            frm_sz=pfile.acq_x_res*2*pt_sz
        #            echo_size=frm_sz*pfile.acq_y_Res
        #            slice_size=echo_size*nechoes
        #            data_sz=pfile.acq_x_res*2*(pfile.acq_y_Res-1)
                fbin.seek(156)        
                acq_x_res=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(180)
                acq_y_Res=struct.unpack('<h',fbin.read(2))[0]
                fbin.seek(280)
                bandwidth=struct.unpack('<f',fbin.read(4))[0]
                
                fbin.seek(296)
                ws_nsa=struct.unpack('<f',fbin.read(4))[0]
                
            ws_avgs=int(ws_nsa)/int(navs)
    
            frm_sz=acq_x_res*2*pt_sz
            echo_size=frm_sz*acq_y_Res
            slice_size=echo_size*nechoes
            data_sz=acq_x_res*2*(acq_y_Res-1)
            #off_raw is the offset in bytes to the start of the raw data
            off_raw=hdr_sz+frm_sz
            
            w_avgs=acq_y_Res-1-ws_avgs
            print('Number of water ref frames : '+str(w_avgs))
            print('Number of data frames : '+str(ws_avgs))
            
            fbin.seek(off_raw)
            raw_data=np.zeros(data_sz)
            frame_data=np.zeros(shape=(int(acq_y_Res-1),int(acq_x_res),int(n_rcv)),dtype=np.int64)
            frame_data=frame_data.view(np.complex64)
            rot_frame_data=np.zeros(shape=(int(acq_y_Res-1),int(acq_x_res),int(n_rcv)),dtype=np.float64)
            rot_frame_data=rot_frame_data.view(np.complex64)
            fid_norm=np.zeros(shape=(int(acq_y_Res-1),int(acq_x_res),int(n_rcv)),dtype=np.float64)
            fid_norm=fid_norm.view(np.complex64)
            summed_signal=np.zeros(shape=(int(acq_y_Res-1)*int(acq_x_res)),dtype=np.float64)
            summed_signal=summed_signal.view(np.complex64)
            
            for receiver in range(0,n_rcv):
                fbin.seek(off_raw+(slice_size*receiver))
                for element in range(0,data_sz):
                    raw_data[element]=struct.unpack('<i',fbin.read(4))[0]
                for frm in range(0,int(acq_y_Res-1)):
                    row_off=frm*acq_x_res*2
                    for pt in range(0,int(acq_x_res)):
                        frame_data[frm,pt,receiver]=raw_data[(2*pt)+row_off]+1j*raw_data[(2*pt)+1+row_off]
            fbin.close()
            amp=np.zeros(n_rcv,dtype=np.int64)
            amp=amp.view(np.complex64)
            amp=frame_data[0,5,:]
            ang=np.zeros(n_rcv)
            fid_w=np.zeros(n_rcv)
            for n in range(0,n_rcv):
                ang[n]=cmath.phase(list(frame_data[0,5,:])[n])
    #            print(ang)
            ph_dif=ang-ang[0]
            
            for receiver in range(0,n_rcv):
                rot_frame_data[:,:,receiver]=frame_data[:,:,receiver]*np.exp(-1j*ph_dif[receiver])
            for receiver in range(0,n_rcv):
                fid_w[receiver]=abs(amp[receiver])/np.sqrt(sum(abs(amp*amp)))
    #            fid_w[receiver]=abs(amp[receiver])/sum(abs(amp))
    #            fid_w=np.max(np.abs(frame_data[1,:,:]),axis=0)/np.sqrt(np.sum(np.max(np.abs(frame_data[1,:,:]),axis=0)*np.max(np.abs(frame_data[1,:,:]),axis=0)))
    #            fid_w=np.abs(np.max(frame_data[0,:,:],axis=0))/(np.sum(np.abs(np.max(frame_data[0,:,:],axis=0))))
                fid_norm[:,:,receiver]=rot_frame_data[:,:,receiver]*fid_w[receiver]
            summed_signal=np.sum(fid_norm,axis=2)
            #fbin.close()
            #raw_data=raw_data.astype(np.int64)
            print('coil weightings:')
            print(fid_w)
    
            output_data_ws=[]
            for pt in range(w_avgs*int(acq_x_res),np.size(summed_signal)):
                output_data_ws.append(np.float64(np.imag(summed_signal.flatten()[pt])))
                output_data_ws.append(np.float64(np.real(summed_signal.flatten()[pt])))
                        
            output_data_w=[]
            for pt in range(0,w_avgs*int(acq_x_res)):
                output_data_w.append(np.float64(np.imag(summed_signal.flatten()[pt])))
                output_data_w.append(np.float64(np.real(summed_signal.flatten()[pt])))
    
            file_meta = Dataset()
            file_meta.MediaStorageSOPClassUID = 'MRSpectroscopyStorage'
            file_meta.MediaStorageSOPInstanceUID = dicom.UID.generate_uid()
            file_meta.ImplementationClassUID = dicom.UID.generate_uid()
            ds_ws = FileDataset(fname+'_dcm', {},file_meta = file_meta,preamble="\0"*128)
            ds_ws.Modality = 'MR'
            ds_ws.ContentDate = str(datetime.date.today()).replace('-','')
            ds_ws.ContentTime = str(time.time()) #milliseconds since the epoch
            ds_ws.StudyInstanceUID = dicom.UID.generate_uid()
            ds_ws.SeriesInstanceUID = dicom.UID.generate_uid()
            ds_ws.SOPInstanceUID = dicom.UID.generate_uid()
            ds_ws.SOPClassUID = 'MRSpectroscopyStorage'
            ds_ws.SecondaryCaptureDeviceManufctur = 'Python 2.7.3'
            
            ds_ws.VolumeLocalizationTechnique = seqtype
            ds_ws.RepetitionTime = tr/1000
            
            ## These are the necessary imaging components of the FileDataset object.
            ds_ws.Columns = 1
            ds_ws.Rows = 1
            ds_ws.DataPointColumns = int(acq_x_res)
            ds_ws.SpectroscopyAcquisitionDataColumns = ds_ws.DataPointColumns
            ds_ws.DataPointRows = ws_avgs
            ds_ws.SpectroscopyData = output_data_ws
            ds_ws.ImageType = ['ORIGINAL', 'PRIMARY', 'SPECTROSCOPY', 'NONE']
            ds_ws.SpectralWidth = bandwidth
            ds_ws.SeriesNumber = series_no
            ds_ws.ProtocolName = fname.split('\\')[-1].split('.')[0]+'_SVS_TR'+str(int(tr/1000))+'_TE'+str(int(te/1000))
            c_freq2=c_freq/10000000.0
            ds_ws.TransmitterFrequency = c_freq2
            ds_ws.EffectiveEchoTime=te/1000
            ds_ws.EchoTime=te/1000        
            ds_ws.WaterReferencedPhaseCorrection = 'N'
    
            if w_avgs > 0: 
                file_meta_w = Dataset()
                file_meta_w.MediaStorageSOPClassUID = 'MRSpectroscopyStorage'
                file_meta_w.MediaStorageSOPInstanceUID = dicom.UID.generate_uid()
                file_meta_w.ImplementationClassUID = dicom.UID.generate_uid()
                ds_w = FileDataset(fname+'_dcm', {},file_meta = file_meta,preamble="\0"*128)
                ds_w.Modality = 'MR'
                ds_w.ContentDate = str(datetime.date.today()).replace('-','')
                ds_w.ContentTime = str(time.time()) #milliseconds since the epoch
                ds_w.StudyInstanceUID = dicom.UID.generate_uid()
                ds_w.SeriesInstanceUID = dicom.UID.generate_uid()
                ds_w.SOPInstanceUID = dicom.UID.generate_uid()
                ds_w.SOPClassUID = 'MRSpectroscopyStorage'
                ds_w.SecondaryCaptureDeviceManufctur = 'Python 2.7.3'
                ds_w.VolumeLocalizationTechnique = seqtype
                
                ## These are the necessary imaging components of the FileDataset object.
                ds_w.Columns = 1
                ds_w.Rows = 1
                ds_w.DataPointColumns = int(acq_x_res)
                ds_w.SpectroscopyAcquisitionDataColumns = ds_w.DataPointColumns
                ds_w.DataPointRows = w_avgs
                ds_w.SpectroscopyData = output_data_w
                ds_w.ImageType = ['ORIGINAL', 'PRIMARY', 'SPECTROSCOPY', 'NONE']
                ds_w.SpectralWidth = bandwidth
                ds_w.SeriesNumber = series_no
                ds_w.ProtocolName = fname.split('\\')[-1].split('.')[0]+'_SVS_TR'+str(int(tr/1000))+'_TE'+str(int(te/1000))
                c_freq2=c_freq/10000000.0
                ds_w.TransmitterFrequency = c_freq2
                ds_w.EffectiveEchoTime=te/1000
                ds_w.EchoTime=te/1000        
                ds_w.RepetitionTime = tr/1000  
                ds_w.WaterReferencedPhaseCorrection = 'N'
    
    
            if not os.path.exists(str(root_dir)+'/'+str(pat_name)+'_PREPROC_LCM'):
                os.makedirs(str(root_dir)+'/'+str(pat_name)+'_PREPROC_LCM')
#            if not os.path.exists(str(root_dir)+'/'+str(pat_name)+'_LCM_Results'):
#                os.makedirs(str(root_dir)+'/'+str(pat_name)+'_LCM_Results')
            ds_ws.save_as(str(root_dir)+'/'+str(pat_name)+'_PREPROC_LCM/'+str(ds_ws.ProtocolName))

            if w_avgs > 0: 
                ds_w.save_as(str(root_dir)+'/'+str(pat_name)+'_PREPROC_LCM/'+str(ds_w.ProtocolName)+'_WATER')
    
    
        except AttributeError:
            print('...')
        except IOError:
            print 'no such file'
    print('DONE!')