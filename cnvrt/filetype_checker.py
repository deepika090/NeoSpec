# -*- coding: utf-8 -*-

### WHAT'S THE DATA TYPE??###

import dicom
import Tkinter, tkFileDialog, tkMessageBox
import os, os.path
import glob
from gepfile_normsq import process_mrs_ge
from philips_dicom_cl import process_mrs_philips_dicom_cl
from philips_dicom_en import process_mrs_philips_dicom_en
from siemens_csa import process_mrs_siemens_csa
from siemens_nocsa import process_mrs_siemens_nocsa
#from oct2py import octave


def filetype_check():    
    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    dcm_dir = tkFileDialog.askdirectory(parent=root)
    os.chdir(dcm_dir)
    root.attributes("-topmost", 0)
    root.destroy()

    for fname in glob.glob(os.path.join(dcm_dir,'*'))+glob.glob(os.path.join(dcm_dir,'*/*')):
#        print(os.path.split(fname)[1])
  
        if (os.path.split(fname)[1].split('.')[-1] == '7') or \
        (os.path.split(fname)[1].split('.')[-1] == 'anon'):
            print('')
            print('GE P-Files contained in this directory:')
            print(os.path.split(fname)[0])
            print('')
            dgbox = Tkinter.Tk()
            dgbox.geometry('0x0+0+0')
            dgbox.attributes("-topmost", 1)
            dgbox.withdraw()
            cnv_yn=tkMessageBox.askokcancel('Convert to MRS','Convert the GE Pfiles?',parent=dgbox)
            dgbox.attributes("-topmost", 0)
            if cnv_yn == True:
                process_mrs_ge(dcm_dir)
                dgbox.attributes("-topmost", 1)
                tkMessageBox.showinfo('Convert to MRS','Conversion complete',parent=dgbox)                
                dgbox.destroy()
            break
        try:
            d=dicom.read_file(fname)
            if (0x0008,0x0070) in d:
                if d.Manufacturer == 'Philips Medical Systems':
                    if ((0x2005,0x1035) in d) and ((0x0008,0x0008) in d):
                        if d[0x2005,0x1035].value == 'SPECTRA':
                            if (0x5200,0x9229) in d:
                                print('')
                                print('Philips Enhanced DICOM files contained in this directory:')
                                print(os.path.split(fname)[0])
                                print('')
                                dgbox = Tkinter.Tk()
                                dgbox.geometry('0x0+0+0')
                                dgbox.attributes("-topmost", 1)
                                dgbox.withdraw()
                                cnv_yn=tkMessageBox.askokcancel('Convert to MRS','Convert the Philips (Enhanced) DICOM files?',parent=dgbox)
                                dgbox.attributes("-topmost", 0)
        #                        dgbox.destroy()
                                if cnv_yn == True:
                                    process_mrs_philips_dicom_en(dcm_dir)
                                    dgbox.attributes("-topmost", 1)
                                    tkMessageBox.showinfo('Convert to MRS','Conversion complete',parent=dgbox)                
                                    dgbox.destroy()
                                break
                            else:
                                print('')
                                print('Philips Classic DICOM files contained in this directory:')
                                print(os.path.split(fname)[0])
                                print('')
                                dgbox = Tkinter.Tk()
                                dgbox.geometry('0x0+0+0')
                                dgbox.attributes("-topmost", 1)
                                dgbox.withdraw()
                                cnv_yn=tkMessageBox.askokcancel('Convert to MRS','Convert the Philips (Classic) DICOM files?',parent=dgbox)
                                dgbox.attributes("-topmost", 0)
                                if cnv_yn == True:
                                    process_mrs_philips_dicom_cl(dcm_dir)
                                    dgbox.attributes("-topmost", 1)
                                    tkMessageBox.showinfo('Convert to MRS','Conversion complete',parent=dgbox)                
                                    dgbox.destroy()
                                break
                        else:
                            continue
                    else:
                        continue
                elif d.Manufacturer == 'Siemens' or d.Manufacturer == 'SIEMENS':
                    if (0x0029,0x1008) in d:
                        print('')
                        print('Siemens DICOM files (CSA) contained in this directory:')
                        print(os.path.split(fname)[0])
                        print('')
                        dgbox = Tkinter.Tk()
                        dgbox.geometry('0x0+0+0')
                        dgbox.attributes("-topmost", 1)
                        dgbox.withdraw()
                        cnv_yn=tkMessageBox.askokcancel('Convert to MRS','Convert the Siemens (CSA) DICOM files?',parent=dgbox)
                        dgbox.attributes("-topmost", 0)
                        if cnv_yn == True:
                            process_mrs_siemens_csa(dcm_dir)                        
                            dgbox.attributes("-topmost", 1)
                            tkMessageBox.showinfo('Convert to MRS','Conversion complete',parent=dgbox)                
                            dgbox.destroy()
                        break
                    else:
                        print('')
                        print('Siemens DICOM files (no CSA) contained in this directory:') 
                        print(os.path.split(fname)[0])
                        print('')
                        dgbox = Tkinter.Tk()
                        dgbox.geometry('0x0+0+0')
                        dgbox.attributes("-topmost", 1)
                        dgbox.withdraw()
                        cnv_yn=tkMessageBox.askokcancel('Convert to MRS','Convert the Siemens (no CSA) DICOM files?',parent=dgbox)
                        dgbox.attributes("-topmost", 0)
                        if cnv_yn == True:
                            process_mrs_siemens_nocsa(dcm_dir)                          
                            dgbox.attributes("-topmost", 1)
                            tkMessageBox.showinfo('Convert to MRS','Conversion complete',parent=dgbox)                
                            dgbox.destroy()
                        break
#                break
#                else:
#                    continue
        except:
            print('...looking for files for conversion...')
            
    os.chdir(os.path.split(dcm_dir)[0])