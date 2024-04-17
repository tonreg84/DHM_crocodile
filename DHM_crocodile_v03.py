"""
DHM crocodile
 Autor: tonreg, team UMI, CNP-CHUV Lausanne
 
 Version 03 - 16.04.2024

 This program is used to reduce the number of holograms recorded during an experience with a LynceeTec DHM.
 
 The program will reduce the frame rate by the given factor RFR (integer greater than 1).
 The program will average over a given number of holograms (NAV, positive integer).
 You can chose RFR and NAV and if the initial hologram files will be overwritten or if the new ones will be saved in a new folder.
 The new frame rate equals the initial frame rate divided by RFR.
 The program creates a new timestamps file where the timestamps correspond to the new frame rate. A new timestamp "n" corresponds to the intial timestamp n*RFR+int(NAV/2) (n=0,1,2,...).
"""

import os
import PySimpleGUI as simgui
from PROD_croco import PROD_croco

from numpy import single
from numpy import array

#initialise some variables
tsstring='No timestamps file selected.\n'
displaytext_RFR=''
displaytext_NAV=''
displaytext_new_N=''
tsfwithness=None

#info window
with open('info.txt') as f:
    infotext=f.read()
f.close()
#infotext='DHM file manager - version 01 - 15.03.2024\n Autor: Gernot Scheerer, team UMI, CNP-CHUV Lausanne\n gernot.scheerer@hotmail.de\n\nThis program is used to average holograms recorded during one experience with a LynceeTec DHM.\nYou can chose how many holograms will be averaged and if the old holos will be overwritten or if the new ones go into a new folder.'

# window layout
files_and_parameter = [
    [simgui.Button(button_text='Info',enable_events=True, key="infobutton"),
    ],
    [simgui.Text("   "),],
    [simgui.Text("Chose a folder with holograms:"),],
    [simgui.In(size=(40, 1), enable_events=True, key="holofolder"),
     simgui.FolderBrowse(),
    ],
    [simgui.Text("Chose the corresponding timestamps file:"),],
    [simgui.In(size=(40, 1), enable_events=True, key="timefilepath"),
     simgui.FileBrowse(),
    ],
    [simgui.Text("   "),
    ],
    [simgui.Text("Reduce frame rate by factor "),
      simgui.In(size=(5, 1), enable_events=True, key="reduceFrate"),
     ],
     [simgui.Text("   "),
     ],
    [simgui.Text("Averaging over"),
     simgui.In(size=(5, 1), enable_events=True, key="NAverage"),
     simgui.Text("holograms"),
    ],
    [simgui.Text("   "),
    ],
    [simgui.Checkbox("Overwrite intial holograms", enable_events=True, key='overwrite'),
    ],
    [simgui.Checkbox("Write into new folder: ", enable_events=True, key='newfolder'),],
    [simgui.Text("  "),simgui.In(size=(37, 1), enable_events=True, key="outfolder"),
     simgui.FolderBrowse(),],
    [simgui.Text("   "),
    ],
    [simgui.Button("Start", enable_events=True, key='start'),
     simgui.Text("                                                           "),
     simgui.Button("Cancel", enable_events=True, key='cancel'),
    ],
    ]

timestampsdisplay = [
     [simgui.Text("Timestamps:")],
     [simgui.Multiline(default_text='No timestamps file selected.\n', enable_events=True, size=(65, 20), key='tsdisp')
     ],
     ]

croco_layout = [
    [
        simgui.Column(files_and_parameter),
        simgui.VSeperator(),
        simgui.Column(timestampsdisplay),
    ]
]

croco_win = simgui.Window("DHM crocodile", croco_layout)

# Main programme
while True:
    event, values = croco_win.read()
    if event == simgui.WIN_CLOSED:
        break
    
    if event == 'cancel':
        break
    
    if event == 'infobutton':
        simgui.popup_scrolled(infotext, title="Info", font=("Arial Bold", 9), size=(100,20))
    
   #display stuff - START
    #create timestamps file info string, get sequence length nImages
    if values['timefilepath'] != "" and tsfwithness != values['timefilepath']:
        tsfwithness = values['timefilepath']
        
        with open(values['timefilepath'], 'r') as infile:
            
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
        
        nImages=len(timestamps) #sequence length
        
        framerate=time/(nImages-1)
        
        if framerate < 1:
            roundFrate=round(framerate, 2)
            tsstring=tsstring+'...\n\nSequence length = '+str(nImages)+'\n\nFrame rate = '+str(roundFrate)+' milliseconds'
        else:
            framerate=time/(nImages-1)/1000
            roundFrate=round(framerate, 2)
            tsstring=tsstring+'...\n\nSequence length = '+str(nImages)+'\n\nFrame rate = '+str(roundFrate)+' seconds' 
    
    #create string "display rate reduction factor RFR"; if RFR is > nImages, set RFR = nImages
    RFR=values['reduceFrate']
    if RFR.isdigit()==True and RFR!='0' and values['timefilepath']!="":
            if int(RFR)<=nImages:
                displaytext_RFR='\nTarget frame rate = '+str( round(framerate*int(RFR),2) )
                displaytext_new_N ='\nTarget sequence length = '+str(int(nImages/int(RFR)))
            else:
                croco_win['reduceFrate'].update(value=nImages)
                displaytext_RFR='\nFrame rate reduction factor cannot be greater than sequence length.'
                displaytext_new_N ='\nTarget sequence length = 1'
    
    #create string "display number of holos to average (NAV)"; if NAV is > nImages, set NAV=nImages
    NAV=values['NAverage']
    if NAV.isdigit()==True and NAV!='0':
        if values['timefilepath'] == "":
            displaytext_NAV='\nAverage over '+NAV+' holograms'
        else:
            if int(NAV)>int(nImages):
                croco_win['NAverage'].update(value=nImages)
                displaytext_NAV='\nNumber of holos to average cannot be greater than sequence length.'
                displaytext_new_N ='\nTarget sequence length = 1'
                displaytext_RFR=''
            else:
                if RFR.isdigit()==True and RFR!='0':
                
                    if int(NAV)<=int(RFR):
                        displaytext_NAV='\nAverage over '+NAV+' holograms'
                    else:
                        displaytext_NAV='\nAverage over '+NAV+' holograms'
                        displaytext_new_N ='\nTarget sequence length = '+str(int(nImages/int(RFR))-int(int(NAV)/int(RFR))+1)
        
                else:
                    displaytext_NAV='\nAverage over '+NAV+' holograms'
                
    croco_win['tsdisp'].update(value=tsstring+'\n'+displaytext_new_N+displaytext_RFR+displaytext_NAV)  
   #display stuff - END
    
    #if tik one box, then set all others to false
    if event == 'overwrite':
        if croco_win['overwrite'].get() == True:
            croco_win['newfolder'].update(value=False)
    if event == 'newfolder':
        if croco_win['newfolder'].get() == True:
            croco_win['overwrite'].update(value=False)
        #suggest a folder for option "Write into new folder" if input folder is choosen
        if croco_win['newfolder'].get() == True and values['holofolder'] != "" and values['outfolder'] == "":
            croco_win['outfolder'].update(value=values['holofolder']+'_averaged')
        
    #start main procedure
    if event == 'start':
        #check if all files and parameter are choosen correctly
        #first check if input folder
        if values['holofolder'] == "": 
            new_in_folder=simgui.popup_get_folder('Please select an input folder:',  title="Error: No input folder selected.")
            croco_win['holofolder'].update(value=new_in_folder)
        else:
            if os.path.isdir(values['holofolder'])==False:
                new_in_folder=simgui.popup_get_folder('\"Hologram folder\" input is not an existing folder. Please select again:',  title="Error: Wrong folder input.")
                croco_win['holofolder'].update(value=new_in_folder)
            else:
                #now check if timestamps file is choosen
                if os.path.isfile(values['timefilepath'])==False:
                    new_in_file=simgui.popup_get_file('\"Timestamps file\" input is not an existing file. Please select again:',  title="Error: Wrong timestamps file input.")
                    croco_win['timefilepath'].update(value=new_in_file)
                else:
                    #now check if the frame rate reduction factor is well a postitive integer
                    RFR=values['reduceFrate']
                    if RFR.isdigit()==False or RFR=='0':
                        simgui.popup_auto_close('The entry for the frame rate reduction factor must be a positive integer!')
                    else:
                        #now check if the number of holograms to average well a postitive integer
                        NAV=values['NAverage']
                        if NAV.isdigit()==False or NAV=='0':
                            simgui.popup_auto_close('The entry for holograms to average must be a positive integer!')
                        else:
                            #now check if output option is selected
                            if croco_win['overwrite'].get() == False and croco_win['newfolder'].get() == False:
                                simgui.popup_auto_close('Error: No output folder option chosen.')
                            else:
                                if croco_win['overwrite'].get() == True:
                                    sure=simgui.popup_yes_no('Are you sure that you want to overwrite the intial holograms?')
                                    if sure=='Yes':
                                        #call the croco proceedure with input overwrite = True
                                        PROD_croco(values['holofolder'],values['holofolder'],True,values['timefilepath'],int(RFR),int(NAV))
                                
                                if croco_win['newfolder'].get() == True:
                                    #check if a new folder is chosen correctly
                                    if values['outfolder']=='':
                                        simgui.popup_auto_close('Error: No output folder chosen.')
                                    else:
                                        #check if outputfolder exists aready
                                        if os.path.isdir(values['outfolder'])==True:
                                            checkfolder=simgui.popup_ok_cancel("Output folder exits already!\nPress Ok to proceed", "Press cancel to stop",  title="Output folder exits already!")
                                            if checkfolder=="OK":
                                                
                                                if values['outfolder']==values['holofolder']:
                                                    simgui.popup_auto_close('Error: Input and output folder are identic, please select another folder.".')
                                                else:
                                                    #check if outputfolder is empty
                                                    if len(os.listdir(values['outfolder'])) != 0:
                                                        checkfolder=simgui.popup_ok_cancel("Output folder is not empty!\nPress Ok to proceed", "Press cancel to stop",  title="Output folder not empty!")
                                                        if checkfolder=="OK":
                                                            #new folder exists, not empty
                                                            #call the croco proceedure with input overwrite = False
                                                            PROD_croco(values['holofolder'],values['outfolder'],False,values['timefilepath'],int(RFR),int(NAV))
                                                    else:
                                                        #new folder exists, empty
                                                        #call the croco proceedure with input overwrite = False
                                                        PROD_croco(values['holofolder'],values['outfolder'],False,values['timefilepath'],int(RFR),int(NAV))
                                    
                                        else: 
                                            #new folder doesnt exists, create it
                                            #call the croco proceedure with input overwrite = False
                                            os.mkdir(values['outfolder'])
                                            PROD_croco(values['holofolder'],values['outfolder'],False,values['timefilepath'],int(RFR),int(NAV))

croco_win.close()

                            
            
            
        
        
        
        
        
        
        
        

    
