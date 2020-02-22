# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 14:32:03 2015

@author: plally
"""

import numpy as np
import os
#import dicom
import tkFileDialog, tkMessageBox
from mrs_save_raw import mrs2raw,mrs2raw_phantom
from mrs_format import mrs_struct
import matplotlib.figure
import matplotlib.backends.backend_tkagg
import Tkinter

def mrs_save(mrs_data):
    """ SAVE SELECTED RAW SPECTRA TO A NEW DICOM & PROCESSED (FILTERED) DATA TO .RAW FILES
        Both of these are placed in a folder as a 'sister directory' i.e. the 
        _MC_PROCESSED folder is in the parent directory of the DICOM file
    """
    try:

                
        ## work out whether eddy current correction is necessary based on TE        
        if mrs_data.te < 288:
            mrs_data.eddy=tkMessageBox.askyesno('ECC', 'Perform an eddy current correction?')
            if mrs_data.eddy == True:
                try:
                    # get path to water directory for eddy current correction
                    mrs_data.h2o_dir = tkFileDialog.askopenfilename(initialdir=mrs_data.dcm_dir)
                    water_data=mrs_struct(mrs_data.h2o_dir)

        
                    ##Create a new window to display the effects of water filtering          
                    frame = Tkinter.Toplevel()
                    ecc_select_GUI(frame,water_data)
        ### EDDY DIALOGUE BOX TO SELECT AVERAGES ### 



        ### EDDY DIALOGUE BOX TO SELECT AVERAGES ### 



        ### EDDY DIALOGUE BOX TO SELECT AVERAGES ### 
        
        
        
        ### EDDY DIALOGUE BOX TO SELECT AVERAGES ### 
        
                    mrs_data.ecc_cx=mrs_data.raw_cx*np.exp(-1.0j*np.angle(water_data.raw_cx))       
                except:
                    mrs_data.eddy=0
            else: mrs_data.eddy=0
        else: mrs_data.eddy=0


        


        ## save data as raw files

    
    except AttributeError:
        print('PROBLEM SAVING FILE!')
        
        
class ecc_select_GUI:
    def __init__(self, app,mrs_data):
        self.app = app
        self.app.title("Choose water spectra for eddy current correction")
        self.mrs_data=mrs_data
        self.fig=matplotlib.figure.Figure(figsize=(8,6), dpi=80)
        self.splt=self.fig.add_subplot(111)
        self.splt.yaxis.set_visible(False)
#        self.splt.invert_xaxis()
        self.splt.set_xlim(0,self.mrs_data.pts_orig)
        self.canvas=matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=app)
        
        #add toolbar
        self.toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg( self.canvas, app )
        self.toolbar.grid(row=1,column=1, sticky="ew", columnspan=3)
        
        #add plot space
        self.canvas.get_tk_widget().grid(row=2,column=2, sticky="nsew",columnspan=2)
        self.canvas.draw()
        
        #add listbox to display averages separately
        self.listbox = Tkinter.Listbox(app,selectmode=Tkinter.MULTIPLE)
        self.listbox.grid(row=2,column=1, sticky="nsew",rowspan=1)
        self.listbox.bind('<<ListboxSelect>>',self.CurSelect)
        
        #make spectral window largest part
        self.app.grid_rowconfigure(1, weight=0)
        self.app.grid_rowconfigure(2, weight=1)
        self.app.grid_columnconfigure(1, weight=0)
        self.app.grid_columnconfigure(2, weight=1)
        self.fig.tight_layout() 
        
        self.plotlist=[]                    
        self.plotlist_fit=[]                    
        print(type(self.mrs_data.fit))
        for sub in range(0,self.mrs_data.nsa):
            l, = self.splt.plot(np.arange(0,self.mrs_data.pts_orig),np.abs(self.mrs_data.raw_cx[sub,:]), lw=2,color='k',visible=False)
            l_fit, = self.splt.plot(np.arange(2,self.mrs_data.pts_orig),np.abs(self.mrs_data.fit[sub,2:]), lw=1,color='r',visible=False)
            self.plotlist.insert(sub,l)
            self.plotlist_fit.insert(sub,l_fit)
        self.listbox.delete(0, Tkinter.END)
        for item in range(0,self.mrs_data.nsa):
            self.listbox.insert(Tkinter.END, str(item))
        self.fig.canvas.draw()
            
    def CurSelect(self,event):    
        values=[self.listbox.get(idx) for idx in self.listbox.curselection()]
        self.mrs_data.vals = [int(x) for x in values]
        for sub in range(0,self.mrs_data.nsa):
            if sub in self.mrs_data.vals:
                self.plotlist[sub].set_visible(True)
                self.plotlist_fit[sub].set_visible(True)
            else:
                self.plotlist[sub].set_visible(False)
                self.plotlist_fit[sub].set_visible(False)
        self.splt.relim()
        self.fig.canvas.draw()