# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:25:24 2015

@author: plally
"""


import Tkinter
#import matplotlib.pyplot as plt
import FileDialog
import matplotlib.figure
import matplotlib.backends.backend_tkagg
import tkFileDialog,tkMessageBox
import dicom
import numpy
import os
from mrs_format import mrs_struct
from mrs_save_raw import mrs2raw
from zerofiller import zerofill
from water_corr import water_t1_corr,lcm_t1_corr_COMET,lcm_peakareas_COMET
from run_hlsvd import hlsvdfilt,hlsvdquant
from ec_correcter import ec_select,ec_correct
from cnvrt.filetype_checker import filetype_check

nc=25       #NUMBER OF COMPONENTS IN HLSVD FOR RESIDUAL WATER
nc_w=5      #NUMBER OF COMPONENTS IN HLSVD FOR WATER SPECTRA


        

class MRS_GUI:
    def __init__(self, master):

        ##Initiate window for processing
        self.master = master
        self.master.title("MRS Postprocessing")

        ##Setup main window##        
        self.fig=matplotlib.figure.Figure(figsize=(8,6), dpi=80)
        self.splt=self.fig.add_subplot(111)
        self.splt.yaxis.set_visible(False)
        self.splt.invert_xaxis()
        self.splt.set_xlim(20,-10)
        self.canvas=matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=master)
        
        ##Add a toolbar        
        self.toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg( self.canvas, master )
        self.toolbar.grid(row=1,column=1, sticky="ew", columnspan=3)
        
        ##Add main canvas        
        self.canvas.get_tk_widget().grid(row=2,column=2, sticky="nsew",columnspan=2,rowspan=2)
        self.canvas.draw()
        
        ##Add slider for zeroth phase angle        
        self.stheta = Tkinter.Scale(master, from_=-180, to=180,resolution=0.1, orient=Tkinter.HORIZONTAL,label='Phase:')
        self.stheta.set(0)
        self.stheta.grid(row=4,column=2, sticky="nsew",columnspan=1,rowspan=2)
        self.stheta.bind("<B1-Motion>", self.Slide)
        
        ##Add slider for apodisation        
        self.sapod = Tkinter.Scale(master, from_=0, to=10, resolution=0.1,orient=Tkinter.HORIZONTAL,label='Apodisation:')
        self.sapod.set(5)
        self.sapod.grid(row=6,column=2, sticky="nsew",columnspan=1,rowspan=2)      
        self.sapod.bind("<B1-Motion>", self.Slide)   

        ##Add listbox so averages are separate        
        self.listbox = Tkinter.Listbox(master,selectmode=Tkinter.EXTENDED)
        self.listbox.grid(row=2,column=1, sticky="nsew",rowspan=1)
        self.listbox.bind('<<ListboxSelect>>',self.CurSelect)
        
        ##Make spectrum fill window as much as possible        
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_rowconfigure(3, weight=0)
        self.master.grid_columnconfigure(1, weight=0)
        self.master.grid_columnconfigure(2, weight=1)
        self.fig.tight_layout() 

        ##Create an empty list which holds all plots for a given file                
        self.plotlist=[]

        ##Add a menubar with links to conversion scripts etc                
        self.menubar = Tkinter.Menu(self.master)
        self.actionmenu = Tkinter.Menu(self.menubar, tearoff=0)
        self.actionmenu.add_command(label="Open File...", command=self.dicom_master)
        self.actionmenu.add_command(label="Convert Directory for Processing...", command=filetype_check)
        self.actionmenu.add_command(label="Calculate water results...", command=self.WaterCalc)
        self.actionmenu.add_command(label="Calculate concentration from LCM results & water results TRs 1500 & 5000 ...", command=self.ConcCalc)
        self.actionmenu.add_command(label="Calculate concentration from LCM results & water results TRs 1500 & 3500 ...", command=self.ConcCalc3500)		
        self.actionmenu.add_command(label="Calculate PARs from LCM results...", command=self.PARCalc)
        self.master.config(menu=self.menubar)
        self.menubar.add_cascade(label="File", menu=self.actionmenu)

        ##Add buttons for various functions                
        self.button1 = Tkinter.Button(master=master, text='Eddy Current Correction', command=self.ECCorr)
        self.button1.grid(row=3,column=1, sticky="nsew", columnspan=1, rowspan=1)
        self.button2 = Tkinter.Button(master=master, text='Filter Selected Spectra', command=self.hlsvd_filt)
        self.button2.grid(row=4,column=1, sticky="nsew", columnspan=1, rowspan=1)
        self.button3 = Tkinter.Button(master=master, text='Save Selected Spectra', command=self.SaveNewMRS)
        self.button3.grid(row=5,column=1, sticky="nsew", columnspan=1, rowspan=1)
        self.button4 = Tkinter.Button(master=master, text='Zerofill', command=self.ZFill)
        self.button4.grid(row=6,column=1, sticky="nsew", columnspan=1, rowspan=1)
        self.button5 = Tkinter.Button(master=master, text='Truncate', command=self.Trunc)
        self.button5.grid(row=7,column=1, sticky="nsew", columnspan=1, rowspan=1)
#        self.button6 = Tkinter.Button(master=master, text='Fit water spectrum', command=self.hlsvd_water_fit)
#        self.button6.grid(row=8,column=1, sticky="nsew", columnspan=1, rowspan=1)
        
        tkMessageBox.showinfo('MRS version 0.1.1','This software is for research use only')
        
    def dicom_master(self):
        ##Hide any old plots and clear them from memory                        
        for sub in range(0,numpy.size(self.plotlist)):
            self.plotlist[sub].set_visible(False)   #otherwise 'burned' onto canvas
        self.plotlist=[]
        print('---CLEARED PREVIOUS CASES FROM ANALYSIS WINDOW---')
        ##Read the new DICOM file dataset                
        dcm_dir=tkFileDialog.askopenfilename(parent=self.master)
        dcm=dicom.read_file(dcm_dir,force=True)
        os.chdir(os.path.split(dcm_dir)[0])
        print('CURRENTLY ANALYSING ----->        '+os.path.split(dcm_dir)[1])

        ##Create an mrs data structure as defined in mrs_format module                        
        self.mrs_data=mrs_struct(dcm)
        self.mrs_data.dcm_dir=dcm_dir

        ##Repopulate the list of plots with the new dataset                                
        for sub in range(0,self.mrs_data.nsa):
            l, = self.splt.plot(self.mrs_data.ppmscale,numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.raw_cx[sub,:]*numpy.exp(1j*self.stheta.get()-self.sapod.get()*self.mrs_data.fscale/self.mrs_data.bw)))), lw=2, visible=False)
            self.plotlist.insert(sub,l)
            
        ##Repopulate the listbox with the subspectra labels                                        
        self.listbox.delete(0, Tkinter.END)
        for item in range(0,self.mrs_data.nsa):
            self.listbox.insert(Tkinter.END, str(item))

        ##Clear the current canvas to blank      
        self.fig.canvas.draw()
        
    def CurSelect(self,event):    
        ##Obtain the spectra labels which are highlighted                                        
        indices=[self.listbox.get(idx) for idx in self.listbox.curselection()]

        ##Obtain the enumerated spectra labels, ignoring flags                                                
        values=numpy.zeros(numpy.size(indices))
        for n in numpy.arange(numpy.size(indices)):
            values[n]=int(indices[n].split("_")[0])
        self.mrs_data.vals = [int(x) for x in values]
        print(self.mrs_data.vals)

        ##Display highlighted spectra                                                
        for sub in range(0,self.mrs_data.nsa):
            if sub in self.mrs_data.vals:
                self.plotlist[sub].set_visible(True)
            else:
                self.plotlist[sub].set_visible(False)
        self.fig.canvas.draw()

    def Slide(self,event):
        ##Obtain the phase and apodisation factors from the slider        
        th=self.stheta.get()*numpy.pi/180
        ap=self.sapod.get()

        ##Generate dummy variables to speed up plotting                
        cx=self.mrs_data.raw_cx
        f=self.mrs_data.fscale
        bw=self.mrs_data.bw

        ##Plot phased and apodised data                
        for sub in range(0,self.mrs_data.nsa):
            amp=numpy.real(numpy.fft.fftshift(numpy.fft.fft(cx[sub,:]*numpy.exp(1j*th-ap*f/bw))))
            self.plotlist[sub].set_ydata(amp)
        self.fig.canvas.draw()

    def hlsvd_filt(self):
        """Call python wrapper for hlsvd, using 'nc' components
            N.B. 'RAW_CX' WILL NOW BE WATER FILTERED!!!!!!!!!!!!!!!!!!"""                    
        self.mrs_data.raw_cx,self.mrs_data.fit=hlsvdfilt(self.mrs_data,nc,self.mrs_data.vals)

        ##Update plots to reflect effects of water filtration          
        for sub in range(0,self.mrs_data.nsa):
            amp=numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.raw_cx[sub,:]*numpy.exp(1j*self.stheta.get()*numpy.pi/180-self.sapod.get()*self.mrs_data.fscale/self.mrs_data.bw))))
            self.plotlist[sub].set_ydata(amp)

        ##Set the hlsvd flag in the mrs data structure for filtered spectra          
        for n in self.mrs_data.vals:
            self.mrs_data.hlsvd[n]=1

        ##Create a new window to display the effects of water filtering          
        frame = Tkinter.Toplevel()
#        frame.iconbitmap('python.ico')
        hlsvd_GUI(frame,self.mrs_data)

        ##Clear the spectra labels and repopulate with filtering suffix          
        self.listbox.delete(0, Tkinter.END)
        for item in range(0,self.mrs_data.nsa):
            if self.mrs_data.hlsvd[item]==1:
                if self.mrs_data.eddy == 0:
                    self.listbox.insert(Tkinter.END,"%s_FILTERED" % item)
                else:
                    self.listbox.insert(Tkinter.END,"%s_ECC_FILTERED" % item)
            else:
                self.listbox.insert(Tkinter.END, str(item))
                
        ##Update the plot window with the filtered result                          
        self.fig.canvas.draw()

    def hlsvd_water_fit(self):
        """Call python wrapper for hlsvd, using 'nc' components
            N.B. 'RAW_CX' WILL NOW BE WATER FILTERED!!!!!!!!!!!!!!!!!!"""                    
        self.mrs_data.h2o_amp,self.mrs_data.fit=hlsvdquant(self.mrs_data,nc_w,self.mrs_data.vals)

        ##Create a new window to display the effects of water filtering          
        frame = Tkinter.Toplevel()
#        frame.iconbitmap('python.ico')
        hlsvd_quant_GUI(frame,self.mrs_data)

        
    def ZFill(self):
        ##Zerofill the data with a factor of 2  
        self.mrs_data=zerofill(self.mrs_data,2)
        print('No. pts:  '+str(self.mrs_data.pts))

        ##Update the plot to reflect the zerofilling  
        for sub in range(0,self.mrs_data.nsa):
            self.plotlist[sub].set_ydata(numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.raw_cx[sub,:]*numpy.exp(1j*self.stheta.get()*numpy.pi/180-self.sapod.get()*self.mrs_data.fscale/self.mrs_data.bw)))))
            self.plotlist[sub].set_xdata(self.mrs_data.ppmscale)
           
        self.fig.canvas.draw()
        
    def Trunc(self):
        ##Truncate the data with a factor of 0.5  
        self.mrs_data=zerofill(self.mrs_data,0.5)
        print('No. pts:  '+str(self.mrs_data.pts))

        ##Update the plot to reflect the truncation  
        for sub in range(0,self.mrs_data.nsa):
            self.plotlist[sub].set_ydata(numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.raw_cx[sub,:]*numpy.exp(1j*self.stheta.get()*numpy.pi/180-self.sapod.get()*self.mrs_data.fscale/self.mrs_data.bw)))))
            self.plotlist[sub].set_xdata(self.mrs_data.ppmscale)
           
        self.fig.canvas.draw()
    
    def ECCorr(self):
            self.mrs_data,self.water_data=ec_select(self.mrs_data)
            frame = Tkinter.Toplevel()            
            ec_select_GUI(frame,self.water_data)
            frame.mainloop()
            self.mrs_data=ec_correct(self.mrs_data,self.water_data)

            self.listbox.delete(0, Tkinter.END)
            for item in range(0,self.mrs_data.nsa):
                    self.listbox.insert(Tkinter.END,"%s_ECC" % item)

            ##Update the plot to reflect the ECC  
            for sub in range(0,self.mrs_data.nsa):
                self.plotlist[sub].set_ydata(numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.raw_cx[sub,:]*numpy.exp(1j*self.stheta.get()*numpy.pi/180-self.sapod.get()*self.mrs_data.fscale/self.mrs_data.bw)))))
                self.plotlist[sub].set_xdata(self.mrs_data.ppmscale)

            self.fig.canvas.draw()

    def WaterCalc(self):

        water_t1_corr()            

        frame = Tkinter.Tk()
        frame.geometry('0x0+0+0')
        frame.attributes("-topmost", 1)
        frame.withdraw()    
        tkMessageBox.showinfo("Water results", "The water results have been calculated")
        frame.attributes("-topmost", 0)
        frame.destroy()

    def PARCalc(self):

        lcm_peakareas_COMET()            

        frame = Tkinter.Tk()
        frame.geometry('0x0+0+0')
        frame.attributes("-topmost", 1)
        frame.withdraw()    
        tkMessageBox.showinfo("PAR results", "The PAR results have been calculated")
        frame.attributes("-topmost", 0)
        frame.destroy()
        
    def ConcCalc3500(self):
        
		tna_conc=lcm_t1_corr_HELIX_3500()
		
#        tna_conc=lcm_t1_corr_COMET()
#        
#        if resfile1 == resfile2:
        frame2 = Tkinter.Tk()
        frame2.geometry('0x0+0+0')
        frame2.attributes("-topmost", 1)
        frame2.withdraw()    
#            phantom_yn=tkMessageBox.askyesno('Phantom?', 'Is this a phantom?',parent=frame2)
#            frame2.attributes("-topmost", 0)
#            frame2.destroy()
#            
#            if phantom_yn == True:
#                tna_conc=conc_calc_phantom(tna_amp,water_amp)
#                tkMessageBox.showinfo("[tNA] estimation result", "Phantom [tNA] = %.1f mM" % tna_conc)
#                with open(resfile1, 'a') as f:
#                    f.write('tNA Concentration Calculation (PHANTOM)\n')
#                    f.write('[tNA], '+str(tna_conc)+', mM\n')
#                    f.write('\n')                
#            else:
#               tna_conc=conc_calc_neo(tna_amp,water_amp)
        tkMessageBox.showinfo("[tNA] estimation result", "Neonatal [tNA] = %.1f mM" % tna_conc)
        frame2.attributes("-topmost", 0)
        frame2.destroy()
#        with open(resfile1, 'a') as f:
#            f.write('tNA Concentration Calculation (NEONATAL)\n')
#            f.write('[tNA], '+str(tna_conc)+', mM\n')
#            f.write('\n')

	def ConcCalc(self):
        
        tna_conc=lcm_t1_corr_COMET()
#        
#        if resfile1 == resfile2:
        frame2 = Tkinter.Tk()
        frame2.geometry('0x0+0+0')
        frame2.attributes("-topmost", 1)
        frame2.withdraw()    
#            phantom_yn=tkMessageBox.askyesno('Phantom?', 'Is this a phantom?',parent=frame2)
#            frame2.attributes("-topmost", 0)
#            frame2.destroy()
#            
#            if phantom_yn == True:
#                tna_conc=conc_calc_phantom(tna_amp,water_amp)
#                tkMessageBox.showinfo("[tNA] estimation result", "Phantom [tNA] = %.1f mM" % tna_conc)
#                with open(resfile1, 'a') as f:
#                    f.write('tNA Concentration Calculation (PHANTOM)\n')
#                    f.write('[tNA], '+str(tna_conc)+', mM\n')
#                    f.write('\n')                
#            else:
#               tna_conc=conc_calc_neo(tna_amp,water_amp)
        tkMessageBox.showinfo("[tNA] estimation result", "Neonatal [tNA] = %.1f mM" % tna_conc)
        frame2.attributes("-topmost", 0)
        frame2.destroy()
#        with open(resfile1, 'a') as f:
#            f.write('tNA Concentration Calculation (NEONATAL)\n')
#            f.write('[tNA], '+str(tna_conc)+', mM\n')
#            f.write('\n')
                        
          
    def SaveNewMRS(self):
        """ SAVE SELECTED RAW SPECTRA TO A NEW DICOM & PROCESSED (FILTERED) DATA TO .RAW FILES"""
        try:

            ## create a new directory for the motion corrected files
            mc_dir=(os.path.split(self.mrs_data.dcm_dir)[0] + '_Ready')
            if not os.path.exists(mc_dir):
                try:            
                    os.makedirs(mc_dir)
                except IOError:
                    print "Sorry, you cannot create a new folder in this location"
    
            ## new folders will have base filename_MC_avgs
            fname_new=(os.path.split(self.mrs_data.dcm_dir)[1]+'_MC_'+str(numpy.size(self.mrs_data.vals)))      
            
            ## create individual RAW directories
            raw_dir=os.path.join(mc_dir,fname_new+'_RAW')
            if not os.path.exists(raw_dir):
                try: 
                    os.makedirs(raw_dir)
                except IOError:
                    print "Sorry, you cannot create a new folder in this location"

#            frame2 = Tkinter.Tk()
#            frame2.geometry('0x0+0+0')
#            frame2.attributes("-topmost", 1)
#            frame2.withdraw()    
#            self.mrs_data.phantom=tkMessageBox.askyesno('Phantom?', 'Is this a phantom?',parent=frame2)
#            frame2.attributes("-topmost", 0)
#            frame2.destroy()
#            if self.mrs_data.phantom == True:
#                mrs2raw_phantom(self.mrs_data,raw_dir,fname_new)
#            else: mrs2raw(self.mrs_data,raw_dir,fname_new)
            mrs2raw(self.mrs_data,raw_dir,fname_new)
            frame2 = Tkinter.Tk()
            frame2.geometry('0x0+0+0')
            frame2.attributes("-topmost", 1)
            frame2.withdraw()    
            tkMessageBox.showinfo('Saved', 'This dataset has been saved.',parent=frame2)
            frame2.attributes("-topmost", 0)
            frame2.destroy()
        except:
             print('Error saving data...')

class hlsvd_GUI:
    def __init__(self, app,mrs_data):
        self.app = app
        self.app.title("HLSVD Results")
        self.mrs_data=mrs_data
        self.fig=matplotlib.figure.Figure(figsize=(8,6), dpi=80)
        self.splt=self.fig.add_subplot(111)
        self.splt.yaxis.set_visible(False)
        self.splt.invert_xaxis()
        self.splt.set_xlim(20,-10)
        self.canvas=matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=app)
        
        #add toolbar
        self.toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg( self.canvas, app )
        self.toolbar.grid(row=1,column=1, sticky="ew", columnspan=3)
        
        #add plot space
        self.canvas.get_tk_widget().grid(row=2,column=2, sticky="nsew",columnspan=2)
        self.canvas.draw()
        
        #add listbox to display averages separately
        self.listbox = Tkinter.Listbox(app,selectmode=Tkinter.EXTENDED)
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
            l, = self.splt.plot(self.mrs_data.ppmscale,numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.raw_cx[sub,:]))), lw=2,color='k',visible=False)
            l_fit, = self.splt.plot(self.mrs_data.ppmscale,numpy.real(numpy.fft.fftshift(numpy.fft.fft(self.mrs_data.fit[sub,:]))), lw=1,color='r',visible=False)
            self.plotlist.insert(sub,l)
            self.plotlist_fit.insert(sub,l_fit)
        self.listbox.delete(0, Tkinter.END)
        for item in range(0,self.mrs_data.nsa):
            self.listbox.insert(Tkinter.END, item)
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


class hlsvd_quant_GUI:
    def __init__(self, app,mrs_data):
        self.app = app
        self.app.title("HLSVD Quantification Results")
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
        self.listbox = Tkinter.Listbox(app,selectmode=Tkinter.EXTENDED)
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
            l, = self.splt.plot(numpy.arange(0,self.mrs_data.pts_orig),numpy.abs(self.mrs_data.raw_cx[sub,:]), lw=2,color='k',visible=False)
            l_fit, = self.splt.plot(numpy.arange(2,self.mrs_data.pts_orig),numpy.abs(self.mrs_data.fit[sub,2:]), lw=1,color='r',visible=False)
            self.plotlist.insert(sub,l)
            self.plotlist_fit.insert(sub,l_fit)
        self.listbox.delete(0, Tkinter.END)
        for item in range(0,self.mrs_data.nsa):
            self.listbox.insert(Tkinter.END, str(item)+' = '+str(numpy.abs(self.mrs_data.h2o_amp[item])))
        self.fig.canvas.draw()
            
    def CurSelect(self,event):    
        values_padded=[self.listbox.get(idx) for idx in self.listbox.curselection()]
        values=[]
        for val in values_padded:
            values.append(val.split(" = ")[0])
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

class ec_select_GUI:
    def __init__(self, app,water_data):
        self.app = app
        self.app.protocol("WM_DELETE_WINDOW",  self.ec_avsel)
        self.app.title("SELECT THE DATASETS FOR EDDY CURRENT CORRECTION")
        self.water_data=water_data
        self.fig=matplotlib.figure.Figure(figsize=(8,6), dpi=80)
        self.splt=self.fig.add_subplot(111)
        self.splt.yaxis.set_visible(False)
#        self.splt.invert_xaxis()
        self.splt.set_xlim(0,self.water_data.pts_orig)
        self.canvas=matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=app)
        
        #add toolbar
        self.toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg( self.canvas, app )
        self.toolbar.grid(row=1,column=1, sticky="ew", columnspan=3)
        
        #add plot space
        self.canvas.get_tk_widget().grid(row=2,column=2, sticky="nsew",columnspan=2)
        self.canvas.draw()
        
        #add listbox to display averages separately
        self.listbox = Tkinter.Listbox(app,selectmode=Tkinter.EXTENDED)
        self.listbox.grid(row=2,column=1, sticky="nsew",rowspan=1)
        self.listbox.bind('<<ListboxSelect>>',self.CurSelect)
        
        #make spectral window largest part
        self.app.grid_rowconfigure(1, weight=0)
        self.app.grid_rowconfigure(2, weight=1)
        self.app.grid_columnconfigure(1, weight=0)
        self.app.grid_columnconfigure(2, weight=1)
        self.fig.tight_layout() 

        #make button for selecting         
        self.button1 = Tkinter.Button(master=app, text='Select', command=self.ec_avsel)
        self.button1.grid(row=3,column=1, sticky="nsew", columnspan=1, rowspan=1)        
        
        self.plotlist=[]                    
        for sub in range(0,self.water_data.nsa):
            l, = self.splt.plot(numpy.arange(0,self.water_data.pts_orig),numpy.abs(self.water_data.raw_cx[sub,:]), lw=2,color='k',visible=False)
            self.plotlist.insert(sub,l)
        self.listbox.delete(0, Tkinter.END)
        for item in range(0,self.water_data.nsa):
            self.listbox.insert(Tkinter.END, str(item))
        self.fig.canvas.draw()
            
    def CurSelect(self,event):    
        values=[self.listbox.get(idx) for idx in self.listbox.curselection()]
        self.water_data.vals = [int(x) for x in values]
        for sub in range(0,self.water_data.nsa):
            if sub in self.water_data.vals:
                self.plotlist[sub].set_visible(True)
            else:
                self.plotlist[sub].set_visible(False)
        self.splt.relim()
        self.fig.canvas.draw()
        
    def ec_avsel(self):
        self.app.destroy()
        self.app.quit()
        


root = Tkinter.Tk()
#root.iconbitmap('python.ico')
my_gui = MRS_GUI(root)
root.mainloop()