# -*- coding: utf-8 -*-
"""
Created on Mon Oct 01 18:34:47 2018

@author: plall
"""

import numpy as np
import os
import Tkinter
import tkFileDialog
import dicom
import matplotlib
from mrs_format import mrs_struct
from run_hlsvd import hlsvdquant
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

np.set_printoptions(precision=15)
nc_w=5

def water_t1_corr():

    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    water1 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE WATER DICOM WITH TR=1500')
    water_dir = os.path.split(water1)[0]
    os.chdir(water_dir)
    res_dir=water_dir+'_Results'
    water2 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE WATER DICOM WITH TR=5000')
    root.attributes("-topmost", 0)
    root.destroy()
    
    
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    
    water_data = {}
    td_list = np.zeros(shape=2)
    amp_list = np.zeros(shape=2)
    
    water_data[0]=mrs_struct(dicom.read_file(water1))
    water_data[1]=mrs_struct(dicom.read_file(water2))
    
    frame1 = Tkinter.Toplevel()            
    water_select_GUI(frame1,water_data[0])
    frame1.mainloop()
    frame2 = Tkinter.Toplevel()            
    water_select_GUI(frame2,water_data[1])
    frame2.mainloop()    
    


    for w in range(0,2):
        amp_list[w]=np.sum(np.abs(hlsvdquant(water_data[w],nc_w,water_data[w].vals)[0]))/np.size(water_data[w].vals)
#        print(amp_list[w])
    td_list = [1470,4970]
            
    plt.scatter(td_list,amp_list)
    
    m0_est,t1_est=np.square(curve_fit(t1_curve,td_list,amp_list,p0=[np.max(amp_list),np.sqrt(1500)])[0])
    
    plt.plot(np.arange(0,10000),t1_curve(np.arange(0,10000),np.sqrt(m0_est),np.sqrt(t1_est)))
    
    axes=plt.gca()
    axes.set_xlim(0,10000)
    axes.set_ylim(0,m0_est)
    axes.set_ylabel('Water Signal Intensity')
    axes.set_xlabel('Repetition Time (ms)')
    axes.set_title('Water Relaxation Curve')
    resfile=os.path.abspath(res_dir + '/water_table.txt')
        
    with open(resfile, 'w') as f:
        f.write('Water Fit Results\n')
        f.write('Water@TR1500, '+str(amp_list[0])+'\n')
        f.write('Water@TR5000, '+str(amp_list[1])+'\n')        
        f.write('Water@TRinf, '+str(m0_est)+'\n')
        f.write('Water T1, '+str(t1_est)+'\n')
        f.write('\n')


def lcm_peakareas_COMET():

    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    table1 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE TE=288 LCM RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    table_dir = os.path.split(table1)[0]
    os.chdir(table_dir)
    root.attributes("-topmost", 0)
    root.destroy()
    

    searchfile = open(table1,'r')
    for line in searchfile:
        if " NAA+NAAG" in line: 
            tna_area=float(line.split()[0])
            break
    searchfile = open(table1,'r')
    for line in searchfile:
        if " Lac+Thr" in line: 
            tlac_area=float(line.split()[0])
            break    
    searchfile = open(table1,'r')
    for line in searchfile:
        if " Cho " in line: 
            tcho_area=float(line.split()[0])*3.0
            break    
    searchfile = open(table1,'r')
    for line in searchfile:
        if " Cr+PCr" in line: 
            tcr_area=float(line.split()[0])
            break    
        
    parresfile=os.path.abspath(table_dir + '/PARs.csv')
    
    with open(parresfile, 'w') as f:
        f.write('Areas From LCM Results\n')
        f.write('tNA area, '+str(tna_area)+'\n')
        f.write('tCho area, '+str(tcho_area)+'\n')        
        f.write('tCr area, '+str(tcr_area)+'\n')
        f.write('tLac area, '+str(tlac_area)+'\n')
        f.write('\n')
        f.write('Peak Area Ratios\n')        
        f.write('tLac/tNA, '+str(tlac_area/tna_area)+'\n')
        f.write('tNA/tCho, '+str(tna_area/tcho_area)+'\n')
        f.write('tNA/tCr, '+str(tna_area/tcr_area)+'\n')
        
        
def lcm_t1_corr_COMET():

    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    table1 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE TR=1500 LCM RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    table_dir = os.path.split(table1)[0]
    os.chdir(table_dir)
    table2 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE TR=5000 LCM RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    table3 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE WATER RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    root.attributes("-topmost", 0)
    root.destroy()
    
    amp_list = np.zeros(shape=2)
    water_amp = np.zeros(shape=1)
    
    searchfile = open(table1,'r')
    for line in searchfile:
        if "NAA+NAAG" in line: 
            amp_list[0]=float(line.split()[0])
            break
    searchfile = open(table2,'r')
    for line in searchfile:
        if "NAA+NAAG" in line: 
            amp_list[1]=float(line.split()[0])
            break    
    searchfile = open(table3,'r')
    for line in searchfile:
        if "Water@TRinf" in line: 
            water_amp=float(line.split()[1])
            break    
        
    
    td_list = [1470,4970]
    
    plt.scatter(td_list,amp_list)
    
    tna_amp,tna_t1=np.square(curve_fit(t1_curve,td_list,amp_list,p0=[np.max(amp_list),np.sqrt(1500)])[0])
    
    plt.plot(np.arange(0,10000),t1_curve(np.arange(0,10000),np.sqrt(tna_amp),np.sqrt(tna_t1)))
    
    axes=plt.gca()
    axes.set_xlim(0,10000)
    axes.set_ylim(0,tna_amp)    
    axes.set_ylabel('tNA Signal Intensity')
    axes.set_xlabel('Repetition Time (ms)')
    axes.set_title('tNA Relaxation Curve')
#    return(m0_est,t1_est)
    
#def conc_calc_phantom(tna_amp,water_amp):
#    lcm_cali_factor=0.500801282
#    water_conc=55509.29781
#
#    tna_h2o_ratio = ((tna_amp*3.0)/water_amp)*lcm_cali_factor
#    
#    tna_conc = tna_h2o_ratio * water_conc * (2.0/3.0)
#    
#    return(tna_conc)
    
#def conc_calc_neo(tna_amp,water_amp):
    lcm_cali_factor=0.500801282
    water_conc=49070.21926

    tna_h2o_ratio = ((tna_amp*3.0)/water_amp)*lcm_cali_factor
    
    tna_conc = tna_h2o_ratio * water_conc * (2.0/3.0)
    
    
    resfile=os.path.abspath(table_dir + '/results.csv')
    
    with open(resfile, 'w') as f:
        f.write('tNA Fit Results\n')
        f.write('tNA@TR1500, '+str(amp_list[0])+'\n')
        f.write('tNA@TR5000, '+str(amp_list[1])+'\n')        
        f.write('tNA@TRinf, '+str(tna_amp)+'\n')
        f.write('tNA T1, '+str(tna_t1)+'\n')
        f.write('Water@TRinf, '+str(water_amp)+'\n')
        f.write('\n')
        f.write('[tNA], '+str(tna_conc)+'\n')
    
    return(tna_conc)
    
	
def lcm_t1_corr_HELIX_3500():

    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    table1 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE TR=1500 LCM RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    table_dir = os.path.split(table1)[0]
    os.chdir(table_dir)
    table2 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE TR=5000 LCM RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    table3 = tkFileDialog.askopenfilename(parent=root,title='CHOOSE WATER RESULTS TABLE',filetypes=[("Table file", "*table.txt")])
    root.attributes("-topmost", 0)
    root.destroy()
    
    amp_list = np.zeros(shape=2)
    water_amp = np.zeros(shape=1)
    
    searchfile = open(table1,'r')
    for line in searchfile:
        if "NAA+NAAG" in line: 
            amp_list[0]=float(line.split()[0])
            break
    searchfile = open(table2,'r')
    for line in searchfile:
        if "NAA+NAAG" in line: 
            amp_list[1]=float(line.split()[0])
            break    
    searchfile = open(table3,'r')
    for line in searchfile:
        if "Water@TRinf" in line: 
            water_amp=float(line.split()[1])
            break    
        
    
    td_list = [1470,3470]
    
    plt.scatter(td_list,amp_list)
    
    tna_amp,tna_t1=np.square(curve_fit(t1_curve,td_list,amp_list,p0=[np.max(amp_list),np.sqrt(1500)])[0])
    
    plt.plot(np.arange(0,10000),t1_curve(np.arange(0,10000),np.sqrt(tna_amp),np.sqrt(tna_t1)))
    
    axes=plt.gca()
    axes.set_xlim(0,10000)
    axes.set_ylim(0,tna_amp)    
    axes.set_ylabel('tNA Signal Intensity')
    axes.set_xlabel('Repetition Time (ms)')
    axes.set_title('tNA Relaxation Curve')
#    return(m0_est,t1_est)
    
#def conc_calc_phantom(tna_amp,water_amp):
#    lcm_cali_factor=0.500801282
#    water_conc=55509.29781
#
#    tna_h2o_ratio = ((tna_amp*3.0)/water_amp)*lcm_cali_factor
#    
#    tna_conc = tna_h2o_ratio * water_conc * (2.0/3.0)
#    
#    return(tna_conc)
    
#def conc_calc_neo(tna_amp,water_amp):
    lcm_cali_factor=0.500801282
    water_conc=49070.21926

    tna_h2o_ratio = ((tna_amp*3.0)/water_amp)*lcm_cali_factor
    
    tna_conc = tna_h2o_ratio * water_conc * (2.0/3.0)
    
    
    resfile=os.path.abspath(table_dir + '/results.csv')
    
    with open(resfile, 'w') as f:
        f.write('tNA Fit Results\n')
        f.write('tNA@TR1500, '+str(amp_list[0])+'\n')
        f.write('tNA@TR3500, '+str(amp_list[1])+'\n')        
        f.write('tNA@TRinf, '+str(tna_amp)+'\n')
        f.write('tNA T1, '+str(tna_t1)+'\n')
        f.write('Water@TRinf, '+str(water_amp)+'\n')
        f.write('\n')
        f.write('[tNA], '+str(tna_conc)+'\n')
    
    return(tna_conc)	
	
	
	
def water_t2_corr_phantom():
    
    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    water_list = tkFileDialog.askopenfilenames(parent=root)
    water_dir = os.path.split(water_list[0])[0]
    os.chdir(water_dir)
    root.attributes("-topmost", 0)
    root.destroy()
    
    water_data = {}
    tr_list = np.zeros(shape=len(water_list))
    te_list = np.zeros(shape=len(water_list))
    amp_list = np.zeros(shape=len(water_list))
    
    for w in range(0,len(water_list)):
        water_data[w]=mrs_struct(dicom.read_file(water_list[w]))
        tr_list[w]=water_data[w].tr
        te_list[w]=water_data[w].te
        amp_list[w]=np.mean(np.abs(hlsvdquant(water_data[w],nc_w,np.arange(0,water_data[w].nsa))[0]))
        
    plt.scatter(te_list,amp_list)
    
    m0_est,t2_est=np.square(curve_fit(t2_curve_mono,te_list,amp_list,p0=[np.sqrt(np.max(amp_list)),50])[0])
    
    plt.plot(np.arange(0,1500),t2_curve_mono(np.arange(0,1500),np.sqrt(m0_est),np.sqrt(t2_est)))
    
    axes=plt.gca()
    axes.set_xlim(0,np.max(te_list))
    
    return(m0_est,t2_est)

def water_t2_corr_csf():
    
    # Make a top-level instance and hide in top left corner, get filepath
    root = Tkinter.Tk()
    root.geometry('0x0+0+0')
    root.attributes("-topmost", 1)
    root.withdraw()
    water_list = tkFileDialog.askopenfilenames(parent=root)
    water_dir = os.path.split(water_list[0])[0]
    os.chdir(water_dir)
    root.attributes("-topmost", 0)
    root.destroy()
    
    water_data = {}
    tr_list = np.zeros(shape=len(water_list))
    te_list = np.zeros(shape=len(water_list))
    amp_list = np.zeros(shape=len(water_list))
    
    fig1, (ax1,ax2) = plt.subplots(nrows=1, ncols=2)
    
    for w in range(0,len(water_list)):
        water_data[w]=mrs_struct(dicom.read_file(water_list[w]))
        tr_list[w]=water_data[w].tr
        te_list[w]=water_data[w].te
        amp_list[w]=np.mean(np.abs(hlsvdquant(water_data[w],nc_w,np.arange(0,water_data[w].nsa))[0]))
        ax1.plot(np.arange(0,water_data[w].pts),np.abs(water_data[w].raw_cx[0,:]))
    ax1.set_ylim(bottom=0)
    ax1.set_xlim(left=0)
#    fig2, ax2 = plt.subplots()    
    ax2.scatter(te_list,amp_list)
    
    m0_1_est,t2_1_est,m0_2_est=np.square(curve_fit(t2_curve_biexp,te_list,amp_list,p0=[np.sqrt(np.max(amp_list)),10.0,np.sqrt(np.max(amp_list/100.0))])[0])
    
    ax2.plot(np.arange(0,1500),t2_curve_biexp(np.arange(0,1500),np.sqrt(m0_1_est),np.sqrt(t2_1_est),np.sqrt(m0_2_est)))
    ax2.set_ylim(bottom=0)
    ax2.set_xlim(left=0)
    return(m0_1_est,t2_1_est,m0_2_est)

    
def t1_curve(td,m0,t1):
    return np.square(m0)*(1 - np.exp(-td/np.square(t1)))

def t2_curve_mono(te,m0,t2):
    return np.square(m0)*np.exp(-te/np.square(t2))

def t2_curve_biexp(te,m0_1,t2_1,m0_2):
    return (np.square(m0_1)*np.exp(-te/np.square(t2_1)))+(np.square(m0_2)*np.exp(-te/500.0))


class water_select_GUI:
    def __init__(self, app,water_data):
        self.app = app
        self.app.protocol("WM_DELETE_WINDOW",  self.water_avsel)
        self.app.title("SELECT THE DATASETS FOR WATER QUANTIFICATION")
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
        self.button1 = Tkinter.Button(master=app, text='Select', command=self.water_avsel)
        self.button1.grid(row=3,column=1, sticky="nsew", columnspan=1, rowspan=1)        
        
        self.plotlist=[]                    
        for sub in range(0,self.water_data.nsa):
            l, = self.splt.plot(np.arange(0,self.water_data.pts_orig),np.abs(self.water_data.raw_cx[sub,:]), lw=2,color='k',visible=False)
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
        
    def water_avsel(self):
        self.app.destroy()
        self.app.quit()