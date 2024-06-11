"""
DHM crocodile
Autor: tonreg, team UMI, CNP-CHUV Lausanne
 
Version 04 - 04.06.2024

This program is used to reduce the number of holograms recorded during an experience with a LynceeTec DHM.
 
The program will reduce the frame rate by the given factor RFR (positive integer).
The program will average over a given number of holograms NAV (positive integer).
You can chose RFR and NAV and if the initial hologram files will be overwritten or if the new ones will be saved in a new folder.
The new frame rate equals the initial frame rate divided by RFR.
The program creates a new timestamps file where the timestamps correspond to the new frame rate. A new timestamp "n" corresponds to the intial timestamp n*RFR+int(NAV/2) (n=0,1,2,...).
"""

import tkinter as tk
from tkinter import filedialog
import os

from PROD_croco import PROD_croco

from numpy import single
from numpy import array

#initialise some variables
sequence_length=''
framerate=None
tsstring='No timestamps file selected.\n'
displaytext_RFR=''
displaytext_NAV=''
displaytext_new_N=''
in_folder=''
time_file=''

#functions called by the buttons
def exitprog(root):
    root.destroy()
    
#info window
with open('info.txt') as f:
    infotext=f.read()
f.close()
def show_info():
    with open('info.txt') as f:
        infotext=f.read()
    f.close()
    tk.messagebox.showinfo("Info", infotext)
def save_in_folder():
    global in_folder
    in_folder=tk.filedialog.askdirectory(parent=root, title="Chose a folder with holograms")
    #suggest a folder for option "Write into new folder" if input folder is choosen
    if Vnew.get() == True and in_folder != '' and new_entry.get() == "":
        new_entry.insert(0,in_folder+'_averaged')
        
def update_display(event):

    global sequence_length, framerate
    global tsstring, displaytext_RFR, displaytext_NAV, displaytext_new_N
    
    if tsstring != 'No timestamps file selected.\n':
    
        #create string "display rate reduction factor RFR"; if RFR is > sequence_length, set RFR = sequence_length
        RFR=RFR_entry.get()
        if RFR.isdigit()==True and RFR!='0':
            if int(RFR)<=sequence_length:
                displaytext_RFR='\nTarget frame rate = '+str( round(framerate*int(RFR),2) )
                displaytext_new_N ='\nTarget sequence length = '+str(int(sequence_length/int(RFR)))
            else:
                RFR_entry.delete(0,tk.END)
                RFR_entry.insert(0,sequence_length)
                displaytext_RFR='\nFrame rate reduction factor cannot be greater than sequence length.'
                displaytext_new_N ='\nTarget sequence length = 1'
     
        #create string "display number of holos to average (NAV)"; if NAV is > sequence_length, set NAV=sequence_length
        NAV=NAV_entry.get()
        if NAV.isdigit()==True and NAV!='0':
            if int(NAV)>int(sequence_length):
                NAV_entry.delete(0,tk.END)
                NAV_entry.insert(0,sequence_length)
                displaytext_NAV='\nNumber of holos to average cannot be greater than sequence length.'
                displaytext_new_N ='\nTarget sequence length = 1'
                displaytext_RFR=''
            else:
                if RFR.isdigit()==True and RFR!='0':
                    if int(NAV)<=int(RFR):
                        displaytext_NAV='\nAverage over '+NAV+' holograms'
                    else:
                        displaytext_NAV='\nAverage over '+NAV+' holograms'
                        displaytext_new_N ='\nTarget sequence length = '+str(int(sequence_length/int(RFR))-int(int(NAV)/int(RFR))+1)
     
                else:
                    displaytext_NAV='\nAverage over '+NAV+' holograms'
                        
        display.delete(1.0, tk.END)
        display.insert(1.0,tsstring+'\n'+displaytext_new_N+displaytext_RFR+displaytext_NAV)    
        
def save_time_file():
    global time_file, sequence_length, framerate
    global tsstring, displaytext_RFR, displaytext_NAV, displaytext_new_N
    time_file = filedialog.askopenfilename(parent=root, title="Chose the corresponding timestamps file")
    if time_file == None:
        time_file = ''
    #create timestamps string, get sequence length
    if time_file != '':
        with open(time_file, 'r') as infile:
             tsstring=''
             k=0
             timelist=[]
             for line in infile:
                 if k <= 9:
                     tsstring=tsstring+line
                     
                 # Split the line into a list of numbers
                 numbers = line.split()
                 time=single(float(numbers[3]))
                 timelist.append(time)
                 k=k+1          
             timestamps=array(timelist)
     
        sequence_length=len(timestamps)
     
        framerate=time/(sequence_length-1)
     
        if framerate < 1:
            roundFrate=round(framerate, 2)
            tsstring=tsstring+'...\n\nSequence length = '+str(sequence_length)+'\n\nFrame rate = '+str(roundFrate)+' milliseconds'
        else:
            framerate=time/(sequence_length-1)/1000
            roundFrate=round(framerate, 2)
            tsstring=tsstring+'...\n\nSequence length = '+str(sequence_length)+'\n\nFrame rate = '+str(roundFrate)+' seconds' 
    
    event=''
    update_display(event)

def check_option(string):
    global in_folder
    #tik box, set the other to false
    if string=='over':
        if Vover.get() == True:
            Vnew.set(False)
    if string=='new':
        if Vnew.get() == True:
            Vover.set(False)
        #suggest a folder for option "Write into new folder" if input folder is choosen
        if Vnew.get() == True and in_folder != '' and new_entry.get() == "":
            new_entry.insert(0,in_folder+'_averaged')
def get_out_folder():
    out_folder=tk.filedialog.askdirectory(parent=root, title="Chose an output folder")
    new_entry.delete(0,tk.END)
    new_entry.insert(0,out_folder)
    
def start():
    #first check if input folder
    global in_folder
    if os.path.isdir(in_folder)==False: 
        save_in_folder()
    else:
        #now check if timestamps file is choosen
        if os.path.isfile(time_file)==False:
            save_time_file()
        else:
            #now check if the frame rate reduction factor is well a postitive integer
            RFR=RFR_entry.get()
            if RFR.isdigit()==False or RFR=='0':
                tk.messagebox.showinfo('Error', 'The entry for the frame rate reduction factor must be a positive integer!')
            else:
                #now check if the number of holograms to average well a postitive integer
                NAV=NAV_entry.get()
                if NAV.isdigit()==False or NAV=='0':
                    tk.messagebox.showinfo('Error', 'The entry for holograms to average must be a positive integer!')
                else:
                    #now check if output option is selected
                    if Vover.get() == False and Vnew.get() == False:
                        tk.messagebox.showinfo('Error', 'No output folder option chosen.')
                    else:
                        if Vover.get() == True:
                            
                            result = tk.messagebox.askquestion('Overwrite holos?', 'Are you sure that you want to overwrite the intial holograms?')
                            if result == 'yes':
                                #call the croco proceedure with input overwrite = True
                                PROD_croco(in_folder,in_folder,True,time_file,int(RFR),int(NAV),root)
                        
                        else:
                            #check if a new folder is chosen correctly
                            if new_entry.get() =='':
                                tk.messagebox.showinfo('Error', 'No output folder chosen.')
                            else:
                                #check if outputfolder exists aready
                                if os.path.isdir(new_entry.get())==True:
                                    result2 = tk.messagebox.askquestion('Output folder exits already!', 'Output folder exits already.\nDo you want to proceed?')
                                    if result2 == "yes":
                                        if new_entry.get() == in_folder:
                                            tk.messagebox.showinfo('Error', 'Input and output folder are identic, please select another folder.')
                                        else:
                                            #check if outputfolder is empty
                                            if len(os.listdir(new_entry.get())) != 0:
                                                result3=tk.messagebox.askquestion('Output folder is not empty!', 'Output folder is not empty.\nDo you want to proceed?')
                                                if result3 == "yes":
                                                    #new folder exists, not empty
                                                    #call the croco proceedure with input overwrite = False
                                                    PROD_croco(in_folder,new_entry.get(),False,time_file,int(RFR),int(NAV),root)
                                            else:
                                                #new folder exists, empty
                                                #call the croco proceedure with input overwrite = False
                                                PROD_croco(in_folder,new_entry.get(),False,time_file,int(RFR),int(NAV),root)
                            
                                else: 
                                    #new folder doesnt exists, create it
                                    #call the croco proceedure with input overwrite = False
                                    os.mkdir(new_entry.get())
                                    PROD_croco(in_folder,new_entry.get(),False,time_file,int(RFR),int(NAV),root)

#create main window
root = tk.Tk()
root.title("DHM crocodile")

info_button = tk.Button(root, text="Information", width=10, height=1, command=lambda: show_info())

#####################################################################
# Frame to chose input files and parameters
FP_frame = tk.LabelFrame(root, text="Files and parameters")

in_button = tk.Button(FP_frame, text="Chose a folder with holograms", width=32, height=1, command=lambda: save_in_folder())
time_button = tk.Button(FP_frame, text="Chose the corresponding timestamps file", width=32, height=1, command=lambda: save_time_file())

RFR_label = tk.Label(FP_frame, text= "Reduce frame rate by factor")
RFR_entry = tk.Entry(FP_frame,width=10)
NAV_label = tk.Label(FP_frame, text= "Averaging over")
NAV_entry = tk.Entry(FP_frame,width=10)
NAVV_label= tk.Label(FP_frame, text= "holograms")

RFR_entry.bind("<KeyRelease>", update_display)
NAV_entry.bind("<KeyRelease>", update_display)

Vover=tk.BooleanVar()
over = tk.Checkbutton(FP_frame, text="Overwrite intial holograms", variable=Vover, command=lambda: check_option('over'))
Vnew=tk.BooleanVar()
new = tk.Checkbutton(FP_frame, text="Write into new folder:", variable=Vnew, command=lambda: check_option('new'))
new_entry = tk.Entry(FP_frame,width=35)
new_button = tk.Button(FP_frame, text="Browse", width=5, height=1, command=lambda: get_out_folder())

#Frame layout
in_button.grid(row=0, column=0, padx=5, pady=5, sticky='n,w')
time_button.grid(row=1, column=0, padx=5, pady=5, sticky='n,w')

RFR_label.grid(row=2, column=0, padx=5, pady=5, sticky='n,e')
RFR_entry.grid(row=2, column=1, padx=5, pady=5, sticky='n,w')

NAV_label.grid(row=3, column=0, padx=5, pady=5, sticky='n,e')
NAV_entry.grid(row=3, column=1, padx=5, pady=5, sticky='n,w')
NAVV_label.grid(row=3, column=2, padx=5, pady=5, sticky='n,w')

over.grid(row=4, column=0, padx=5, pady=5, sticky='n,w')
new.grid(row=5, column=0, padx=5, pady=5, sticky='n,w')
new_entry.grid(row=6, column=0, padx=5, pady=5, sticky='n,e')
new_button.grid(row=6, column=1, padx=5, pady=5, sticky='n,w')

#####################################################################
start_button = tk.Button(root, text="Croco eat :)", width=10, height=1, command=lambda: start())
exit_button = tk.Button(root, text="Croco out :(", width=10, height=1, command=lambda: exitprog(root))

#####################################################################
# Display frame
display_frame = tk.LabelFrame(root, text="Timestamps:")
display=tk.Text(display_frame, height = 20, width = 65)
display.pack(side="left", padx=5, pady=5)
Font_tuple = ("Arial", "10")
display.configure(font = Font_tuple) 
display.insert(tk.END, "No timestamps file selected.")

###########################################
#Window layout
info_button.grid(row=0, column=0, padx=5, pady=5, sticky='n,w')
FP_frame.grid(row=1, column=0, padx=5, pady=5, sticky='n,w')
start_button.grid(row=2, column=0, padx=5, pady=5, sticky='n,w')
display_frame.grid(row=1, column=1, padx=5, pady=5, sticky='n,w')
exit_button.grid(row=2, column=1, padx=5, pady=5, sticky='n,e')

###########################################

root.mainloop()

###########################################
