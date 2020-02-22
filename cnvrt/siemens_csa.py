# -*- coding: utf-8 -*-

import dicom
#import Tkinter, tkFileDialog
import os, os.path
from dicom.filereader import InvalidDicomError
import glob
import array
import numpy as np
import struct
import gdcm

def process_mrs_siemens_csa(dcm_dir):    
    
#    ###USE THIS FOR DICOM FILES THAT HAVE CSA HEADERS###
#    
#    # Make a top-level instance and hide in top left corner, get filepath
#    root = Tkinter.Tk()
#    root.geometry('0x0+0+0')
#    root.attributes("-topmost", 1)
#    dcm_dir = tkFileDialog.askdirectory(parent=root)
#    root.attributes("-topmost", 0)
#    root.destroy()
    
    root_dir=os.path.abspath(os.path.join(dcm_dir, os.pardir))
    pat_name=os.path.split(os.path.dirname(dcm_dir))[1]
    
    f = file(root_dir + '/preproc_dump.txt', 'w')
    
    l=[]
    for fname in glob.glob(dcm_dir + '/*.dcm'):
        try:
            d = dicom.read_file(fname,force="True")
    #        if d.SoftwareVersions[-3:]=="B17":
            if (0x7fe1,0x1010) in d:
                d.DataPointColumns=len(d[0x7fe1,0x1010].value)/8
                d.DataPointRows=1
                l.append([fname,int(d.SeriesNumber),d.AcquisitionNumber,d.DataPointColumns,d.DataPointRows])
        except AttributeError:
            print('...')
        except IOError:
            print 'no such file'
    
    for nlist in range(0,len(l)):
        if l[nlist][2]==1:
            try:
                
                d = dicom.read_file(l[nlist][0],force='TRUE')
    #            d.SpectroscopyAcquisitionDataColumns = lambda: None
    #            d.SpectroscopyAcquisitionDataColumns = d.DataPointColumns
                d.SpectroscopyAcquisitionDataColumns = l[nlist][3]
    #            d.ProtocolName=str(d.ProtocolName).replace (" ","_")
    #            d.ProtocolName="HELIX"
    
    #            p1 = subprocess.Popen(["gdcmdump", "-C",l[nlist][0]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #            csa1 = p1.communicate()[0]
    #            d.ProtocolName=csa1.split("tProtocolName")[1].split("\t")[2].split("\r")[0].split('"')[2]
    #            print >>f, 'file: '+l[nlist][0]+'\tSeries: '+d.ProtocolName
                #print(l[nlist][0])
    #            if d.WaterReferencedPhaseCorrection =="YES":
    #                ecc_str = 'ECC'
    #            else:
    #                ecc_str = 'NO_ECC'   
                ecc_str='NO_ECC'
#                fname_new=(str(d.SeriesNumber)+'_'+str(d.ProtocolName).replace (" ","_").replace("/","_")+'_'+str(1)+'_'+ecc_str)
    #            if not os.path.exists(root_dir + '/' + pat_name + '_PREPROC_LCM'):
    #                os.makedirs(root_dir + '/' + pat_name + '_PREPROC_LCM')
    #            d.save_as(root_dir + '/' + pat_name + '_PREPROC_LCM/' + fname_new)
                series=l[nlist][1]
                npts=l[nlist][3]
                avg=0
                for plist in range(0,len(l)):
                    if l[plist][1]==series:
                        avg=avg+1
                print(avg)
                fname_new=(str(d.SeriesNumber)+'_'+str(d.ProtocolName).replace (" ","_").replace("/","_")+'_'+str(avg)+'_'+ecc_str)
                spec_data=np.zeros(shape=(avg*npts*2))
                n=[]
                for k in np.arange(0,npts):
                    n.append(struct.unpack('f',d[0x7fe1,0x1010].value[4*k:4*k+4])[0])
                spec_data[0:(npts*2)]=array.array('f',d[0x7fe1,0x1010].value)
    #            spec_data[0:(npts*2)]=d.SpectroscopyData
                for plist in range(0,len(l)):
                    if l[plist][1]==series:
                        print(l[plist][0])
                        try:
                            d_sub = dicom.read_file(l[plist][0])
    #                        d_sub.ProtocolName=str(d_sub.PatientName).replace (" ","_")
                            nsub=int(l[plist][2]-1)
                            spec_data[(nsub*npts*2):((nsub+1)*npts*2)]=array.array('f',d_sub[0x7fe1,0x1010].value)
                            print >>f, 'file: '+l[plist][0]+'\tSeries: '+d_sub.ProtocolName
                            print(l[plist][0])
                        except AttributeError:
                            print('...')
                        except IOError:
                            print 'no such file'
                        except InvalidDicomError:
                            print 'Invalid Dicom file'            
                spec_data_dummy=np.zeros(d.SpectroscopyAcquisitionDataColumns*avg*2)
                spec_data_dummy[0:d.SpectroscopyAcquisitionDataColumns*avg*2:2]=spec_data[1:d.SpectroscopyAcquisitionDataColumns*avg*2:2]
                spec_data_dummy[1:d.SpectroscopyAcquisitionDataColumns*avg*2:2]=spec_data[0:d.SpectroscopyAcquisitionDataColumns*avg*2:2]
                d.SpectroscopyData=list(spec_data_dummy)
    
    
                r = gdcm.Reader()
                r.SetFileName( str(l[nlist][0]) )
                r.Read()
                
                ds = r.GetFile().GetDataSet()
                csa_h1 = gdcm.CSAHeader()
                
                csa1 = csa_h1.GetCSAImageHeaderInfoTag();
                print csa1
    
                if ds.FindDataElement( csa1 ):
                  csa_h1.LoadFromDataElement( ds.GetDataElement( csa1 ) )
                  
                d.EffectiveEchoTime=float(str(csa_h1.GetCSAElementByName( "EchoTime" ).GetValue()))
                d.RepetitionTime=float(str(csa_h1.GetCSAElementByName( "RepetitionTime" ).GetValue()))
                d.TransmitterFrequency=float(str(csa_h1.GetCSAElementByName( "ImagingFrequency" ).GetValue()))
                d.SpectralWidth=1e9/float(str(csa_h1.GetCSAElementByName( "RealDwellTime" ).GetValue()))
                d.EchoTime=d.EffectiveEchoTime
                
                seqtype = str(csa_h1.GetCSAElementByName( "SequenceName" ).GetValue()).split("*")[1]
                
                if seqtype == 'svs_st':
                    d.VolumeLocalizationTechnique = 'STEAM'
                elif seqtype == 'svs_se':
                    d.VolumeLocalizationTechnique = 'PRESS'
                
                if not os.path.exists(root_dir + '/' + pat_name + '_PREPROC_LCM'):
                    os.makedirs(root_dir + '/' + pat_name + '_PREPROC_LCM')
#                if not os.path.exists(root_dir + '/' + pat_name + '_LCM_Results'):
#                    os.makedirs(root_dir + '/' + pat_name + '_LCM_Results') 
                d.save_as(root_dir + '/' + pat_name + '_PREPROC_LCM/' + fname_new)            
            except AttributeError:
                print('...')
            except IOError:
                print 'no such file...'
            except InvalidDicomError:
                print 'Invalid Dicom file'
    
    
    f.close()
    print('DONE!')