def PROD_croco(infolder,outfolder,overwrite_check,timestampsfile,RFR,NAV):
# this procedure is part of the program DHM crocodile 

#  Autor: Gernot Scheerer, team UMI, CNP-CHUV Lausanne
#  gernot.scheerer@hotmail.de
 
#  Version 03 - 16.04.2024

#infolder: string, hologram folder
#outfolder: string, target folder for averaged holograms
#overwrite_check: boolean, if True -> initial holograms will be overwritten
#timestampsfile: string, location of the initial timestamps file
#RFR: integer greater than 1; The program will reduce the frame rate by the given factor RFR.
#NAV: positive integer; The program will average over a given number NAV of holograms.

    from tifffile import imread
    from tifffile import imsave
    import os
    import numpy
    from PySimpleGUI import ProgressBar
    from PySimpleGUI import Text
    from PySimpleGUI import Window
    
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
    if NAV<=RFR:
        images_to_process=int(nImages/RFR)*RFR
    else:
        images_to_process=nImages_new*NAV
    
    ProgLayout = [
        [ProgressBar(images_to_process, orientation='h', expand_x=True, size=(30, 10),  key='prog')],
        [Text('Holos crocodiled: 0 of '+str(images_to_process), key='out', enable_events=True, font=('Arial Bold', 16), justification='center', expand_x=True)]
    ]
    progwin = Window('Crocodile\'s lunch progress', ProgLayout, size=(450, 75), finalize=True)
    event, values = progwin.read(timeout=500)
    
    #averaging the holograms
    for k in range(nImages_new):
        holo_check=True
        
        if NAV<=RFR:
            for i in range(RFR):
                input_file_path=infolder+'/'+str(k*RFR+i).rjust(5, '0')+'_holo.tif'
                
                if i+1 <= NAV:
                    if holo_check==True:
                        holo=imread(input_file_path, key=0).astype(float)
                        holo_check=False
                    else:
                        holo=holo+imread(input_file_path, key=0).astype(float)
                
                if overwrite_check==True:
                    os.remove(input_file_path)
                                
                progwin['prog'].update(current_count=k*RFR+i+1)
                progwin['out'].update('Holos crocodiled: '+str(k*RFR+i+1)+' of '+str(images_to_process))
                
        else:
            for i in range(NAV):
                input_file_path=infolder+'/'+str(k*RFR+i).rjust(5, '0')+'_holo.tif'
                
                if holo_check==True:
                    holo=imread(input_file_path, key=0).astype(float)
                    holo_check=False
                else:
                    holo=holo+imread(input_file_path, key=0).astype(float)
                
                if overwrite_check==True and i <= RFR-1:
                    os.remove(input_file_path)

                progwin['prog'].update(current_count=k*NAV+i+1)
                progwin['out'].update('Holos crocodiled: '+str(k*NAV+i+1)+' of '+str(images_to_process))
            
        holo=holo/NAV
        
        hoholo=numpy.uint8(numpy.round(holo, decimals = 0, out = None))

        output_file_path=outfolder+'/'+str(k).rjust(5, '0')+'_holo_new.tif'
        
        imsave(output_file_path, hoholo, compression=1, append=True, bitspersample=8, planarconfig=1)
    
    if overwrite_check==True:
        for j in range(RFR*nImages_new,nImages):
            input_file_path=infolder+'/'+str(j).rjust(5, '0')+'_holo.tif'
            os.remove(input_file_path)
    
    progwin.close()