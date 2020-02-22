# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 14:32:03 2015

@author: plally
"""

import numpy as np
import dicom
import tkFileDialog, tkMessageBox
from mrs_format import mrs_struct
import Tkinter

def ec_select(mrs_data):
    """ 
    """
    try:                
        ## work out whether eddy current correction is necessary based on TE        
        if mrs_data.te < 288:
            root = Tkinter.Tk()
            root.geometry('0x0+0+0')
            root.attributes("-topmost", 1)
            root.withdraw()            
            mrs_data.eddy=tkMessageBox.askyesno('ECC', 'Perform an eddy current correction?',parent=root)
            if mrs_data.eddy == True:
                try:
                    # get path to water directory for eddy current correction
                    mrs_data.h2o_dir = tkFileDialog.askopenfilename(parent=root,initialdir=mrs_data.dcm_dir)
                    water_data=mrs_struct(dicom.read_file(mrs_data.h2o_dir))
#                    mrs_data.ecc_cx=mrs_data.raw_cx*np.exp(-1.0j*np.angle(water_data.raw_cx))       
                except:
                    mrs_data.eddy=0
            else: mrs_data.eddy=0
            
            root.attributes("-topmost", 0)
            root.destroy()
            
        else: mrs_data.eddy=0

        return(mrs_data,water_data)
    except:
        print("Error selecting water file for eddy current correction!")
        
def ec_correct(mrs_data,water_data):
    """ 
    """
    try:
        phase_corr=np.angle(np.mean(water_data.raw_cx[water_data.vals],axis=0))
        mrs_data.raw_cx=mrs_data.raw_cx*np.exp(-1.0j*phase_corr)       

        return(mrs_data)
    except:
        print("Error running eddy current correction!")