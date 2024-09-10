def PROD_croco(infolder,outfolder,overwrite,timestampsfile,RFR,NAV,master):
# this procedure is part of the program DHM crocodile v04

#infolder: string, hologram folder
#outfolder: string, target folder for averaged holograms
#overwrite: boolean, if True -> initial holograms will be overwritten
#timestampsfile: string, location of the original timestamps file
#RFR: integer greater than 1; The program will reduce the frame rate by the given factor RFR.
#NAV: positive integer; The program will average over a given number NAV of holograms.
    import time as tttime
    from tifffile import imread
    from tifffile import imsave
    import os
    import numpy
    
    from tkinter import ttk, Toplevel, DoubleVar, Label, StringVar
    import threading
    
    #read timestamps from timestampsfile
    with open(timestampsfile, 'r') as infile:
        
        k=0
        timelist=[]
        timestampslist=[]
        for line in infile:
            timestampslist.append(line)
            # Split the line into a list of numbers
            numbers = line.split()
            time=numpy.single(float(numbers[3]))
            timelist.append(time)
            k=k+1          
        timestamps=numpy.array(timelist)
        
    #sequence length
    nImages=len(timestamps) 
    
    #new sequence length:
    if NAV<=RFR:
        nImages_new=int(nImages/RFR)
    else:

        x=nImages-int(nImages/RFR)*RFR

        y=NAV-int(NAV/RFR)*RFR
        
        if y<=x:
            nImages_new=int(nImages/RFR)-int(NAV/RFR)+1
        else:
            nImages_new=int(nImages/RFR)-int(NAV/RFR)
    
    print("New sequence length:", nImages_new)    
    
    #create list of new timestamps and write new timestamps to text file
    tsf_name, tsf_extension = os.path.splitext(timestampsfile)
    new_timestampsfile=tsf_name+'_new.txt'
    with open(new_timestampsfile, 'w') as fileID:
        #new sequence length:
        for k in range(nImages_new):
            TSstr=timestampslist[k*RFR+int(0.5*NAV)]
            #change timestamps running numbers
            TSstr_list=TSstr.split()
            TSstr_new=str(k).rjust(5, '0')
            for i in range(1,len(TSstr_list)):
                TSstr_new=TSstr_new+' '+TSstr_list[i]
            if k!=nImages_new-1:
                TSstr_new=TSstr_new+'\n'
            fileID.write(TSstr_new)
    fileID.close()
    
    #Progress bar
    # Function to update the progress bar 
    def update_progress_bar():
    
        #averaging the holograms
        for k in range(nImages_new):
            holo_check=True
            
            for i in range(NAV):
                input_file_path=infolder+'/'+str(k*RFR+i).rjust(5, '0')+'_holo.tif'
                
                if i+1 <= NAV:
                    if holo_check==True:
                        holo=imread(input_file_path, key=0).astype(float)
                        holo_check=False
                    else:
                        holo=holo+imread(input_file_path, key=0).astype(float)
                
            progress_var.set(k*RFR)  # Update progress bar value
            labelvar.set('Holos crocodiled: '+str(k*RFR)+' of '+str(nImages))
            tttime.sleep(.5)
                              
            holo=holo/NAV
            
            hoholo=numpy.uint8(numpy.round(holo, decimals = 0, out = None))
    
            output_file_path=outfolder+'/'+str(k).rjust(5, '0')+'_holo_new.tif'
            
            imsave(output_file_path, hoholo, compression=1, append=True, bitspersample=8, planarconfig=1)
        
            if overwrite==True:
                for j in range(RFR):
                    file_path=infolder+'/'+str(k*RFR+j).rjust(5, '0')+'_holo.tif'
                    os.remove(file_path)
                    print("Holo removed:", file_path)
                    
        if overwrite==True:
            for i in range(nImages_new*RFR,nImages):
                file_path=infolder+'/'+str(i).rjust(5, '0')+'_holo.tif'
                os.remove(file_path)
                print("Holo removed:", file_path)
            
        progress_window.destroy() 
        
    # Create a new window for the progress bar
    progress_window = Toplevel(master)
    progress_window.geometry("350x100")
    progress_window.title("Crocodile\'s lunch progress")
    
    # Create a progress bar widget
    progress_var = DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, maximum=nImages, variable=progress_var)
    progress_bar.place(x=50, y=30, width=250) 
    
    # Show progress as text
    labelvar = StringVar()
    labelvar.set('Holos crocodiled: 0 of '+str(nImages))
    progress_label = Label(progress_window, textvariable=labelvar)
    progress_label.place(x=50, y=60)
    
    # Run the update in a separate thread to avoid blocking the main thread
    threading.Thread(target=update_progress_bar).start()
    
    progress_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable closing the window using the close button
    progress_window.geometry("+{}+{}".format(master.winfo_rootx() + 50, master.winfo_rooty() + 50))
    progress_window.grab_set()
    master.wait_window(progress_window)
