import MySQLdb as db
import dicom
import numpy as np
import os

def addPixelData():
    con = db.connect('localhost','root','$i_rt_test','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT fk_sop_id, fk_series_id, fk_study_id, fk_patient_id FROM ct_image LIMIT 5')
    tempResult=cur.fetchall()
    fk_sop_ids = [str(x[0]) for x in tempResult]
    fk_series_ids = [str(x[1]) for x in tempResult]
    fk_study_ids = [str(x[2]) for x in tempResult]
    fk_patient_ids = [str(x[3]) for x in tempResult]

    for idx, sop in enumerate(fk_sop_ids):
        pid=fk_patient_ids[idx]
        study=fk_study_ids[idx]
        series=fk_series_ids[idx]
        sop=fk_sop_ids[idx]
        file_path = '/home/dsrt/django/dsrt/dsrt/static/dicom/'+pid+'/'+study+'/'+series+'/'+sop+'.dcm'
        ds=dicom.read_file(file_path)
        pixelData=ds.pixel_array
        if hasattr(ds,'WindowWidth'):
            windowWidth=ds.WindowWidth
        if hasattr(ds,'WindowCenter'):
            windowCenter = ds.WindowCenter
        zIndex =  ds.ImagePositionPatient[2]
        rows = ds.Rows
        columns = ds.Columns
        imageData=[]
        rescaleSlope=ds.RescaleSlope
        rescaleIntercept=ds.RescaleIntercept
        

        pixelData2=(pixelData/np.amax(pixelData))*255
        pixelDataFinal=pixelData2
        #pixelDataRescaled=(pixelData*rescaleSlope)+(rescaleIntercept*np.ones((pixelData.shape)))
        #pixelDataReranged=(pixelData-(np.amin(pixelData)*np.ones((pixelData.shape))))/(np.amax(pixelData)-np.amin(pixelData))
        #pixelDataReranged[np.nonzero(pixelDataReranged>1.0)]=1
        pixelDataFinal[np.nonzero(pixelDataFinal<0)]=0
        t1=np.reshape(pixelDataFinal,rows*columns,order='C')
        t2=np.repeat(t1,3)
        t3=np.reshape(t2,(rows*columns,3),order='C')
        t4=255*np.ones((rows*columns,1))
        t5=np.concatenate((t3,t4),1)
        t6=np.reshape(t5,rows*columns*4,order='C')
        
    print(str(list(pixelData)))
    return

def addZIndex():
    con = db.connect('localhost','root','$i_rt_test','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT fk_sop_id FROM ct_image')
    ids = [int(x[0]) for x in cur.fetchall()]
    for id in ids:
        cur.execute('SELECT imgPosPatZ FROM image_plane_pixel WHERE fk_sop_id="'+str(id)+'"')
        zIndex=cur.fetchall()[0][0]
        sqlString='UPDATE ct_image SET zIndex="'+str(zIndex)+'" WHERE fk_sop_id = "'+str(id)+'"'
        print sqlString
        cur2=con.cursor()
        cur2.execute(sqlString)
        print "executed"
        con.commit()
        
def addImageData():
    con = db.connect('localhost','root','$i_rt_test','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT fk_sop_id, fk_series_id, fk_study_id, fk_patient_id FROM ct_image WHERE fk_sop_id="129"')
    con.close()
    tempResultContainer = cur.fetchall()
    ct_fk_sop_ids=[x[0] for x in tempResultContainer]
    ct_fk_series_ids=[x[1] for x in tempResultContainer]
    ct_fk_study_ids=[x[2] for x in tempResultContainer]
    ct_fk_patient_ids=[x[3] for x in tempResultContainer]
    for idx, sop_id in enumerate(ct_fk_sop_ids):
        ds=dicom.read_file('/home/rt_test/django/rtds/rtds/static/dicom/'+str(ct_fk_patient_ids[idx])+'/'+str(ct_fk_study_ids[idx])+'/'+str(ct_fk_series_ids[idx])+'/'+str(ct_fk_sop_ids[idx])+'.dcm')
        pixelData=ds.pixel_array         
        rows = ds.Rows
        columns = ds.Columns
        pixelData=np.float32(pixelData)
        pixelDataRescaled=(pixelData/np.amax(pixelData))*255	
        pixelDataFinal=pixelDataRescaled
        pixelDataFinal[np.nonzero(pixelDataFinal>255)]=255
        pixelDataFinal[np.nonzero(pixelDataFinal<0)]=0
        t1=np.reshape(pixelDataFinal,rows*columns,order='C')
        t2=np.repeat(t1,3)
        t3=np.reshape(t2,(rows*columns,3),order='C')
        t4=255*np.ones((rows*columns,1))
        t5=np.concatenate((t3,t4),1)
        t6=np.reshape(t5,rows*columns*4,order='C')
        con = db.connect('localhost','root','$i_rt_test','rt_hn')
        cur = con.cursor()
        sqlString='UPDATE ct_image SET width="'+str(columns)+'", height="'+str(rows)+'", pixelData8="'+str(list(t1))+'", jsImageData8="'+str(list(t6))+'" WHERE fk_sop_id="'+str(sop_id)+'"'
        cur.execute(sqlString)
        con.commit()
        con.close()
        print sop_id

def writeJSPixelData():
    pList = [1,3,4,5,7,8,11,12,14,15,16,17,18,19,20,22,23,24,25,27,29,30,31,32,33,34,35,37,38,40,41,45,47,48,49,50,52,53,54,55,56,57,58,60,62,63,65,67,68,69,70,71]
    for fk_patient_id in pList: 
        con = db.connect('localhost','root','$rt_ds_37','rt_hn')
        cur = con.cursor()
        cur.execute('SELECT fk_sop_id, fk_series_id, fk_study_id, fk_patient_id FROM ct_image WHERE fk_patient_id="'+str(fk_patient_id)+'" ORDER BY zIndex DESC')
        con.close()
        tempResultContainer = cur.fetchall()
        ct_fk_sop_ids=[x[0] for x in tempResultContainer]
        ct_fk_series_ids=[x[1] for x in tempResultContainer]
        ct_fk_study_ids=[x[2] for x in tempResultContainer]
        ct_fk_patient_ids=[x[3] for x in tempResultContainer]

    #jsString = ""
        os.makedirs('/home/dsrt/django/dsrt/dsrt/static/jsPixelData/'+str(fk_patient_id)+'/')   
        for idx, sop_id in enumerate(ct_fk_sop_ids):
            ds=dicom.read_file('/home/dsrt/django/dsrt/dsrt/static/dicom/'+str(ct_fk_patient_ids[idx])+'/'+str(ct_fk_study_ids[idx])+'/'+str(ct_fk_series_ids[idx])+'/'+str(ct_fk_sop_ids[idx])+'.dcm')
            pixelData=ds.pixel_array         
            rows = ds.Rows
            columns = ds.Columns
            pixelData=np.float32(pixelData)
        #pixelDataRescaled=(pixelData/np.amax(pixelData))*255	
            pixelDataRescaled=(pixelData/2177)*255	
            pixelDataFinal=pixelDataRescaled
            pixelDataFinal[np.nonzero(pixelDataFinal>255)]=255
            pixelDataFinal[np.nonzero(pixelDataFinal<0)]=0
            t1=np.reshape(pixelDataFinal,rows*columns,order='C')
            t2=np.repeat(t1,3)
            t3=np.reshape(t2,(rows*columns,3),order='C')
            t4=255*np.ones((rows*columns,1))
            t5=np.concatenate((t3,t4),1)
            t6=np.reshape(t5,rows*columns*4,order='C')
            t6 = [round(x,0) for x in t6]
            jsString = "var pix = " + str(list(t6)) + ";\n consolidateImages(pix,"+str(idx)+");"
            f = open("/home/dsrt/django/dsrt/dsrt/static/jsPixelData/"+str(fk_patient_id)+"/"+str(idx)+".js","w")
            f.write(jsString)
            f.close()
            print fk_patient_id, idx

    
    
def checkDose():
    con = db.connect('localhost','root','$rt_ds_37','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT id from dose')
    ids = [int(x[0]) for x in cur.fetchall()]
    for id in ids:
        cur.execute('SELECT GridFrameOffsetVector, ImagePositionPatient FROM dose WHERE fk_patient_id="'+str(id)+'"')
        result=cur.fetchall()
        print result[0]
                   
def addStdROIName():
    con = db.connect('localhost','root','$rt_ds_37','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT id, fk_patient_id, ROIName FROM contour_sequence')
    result = cur.fetchall()
    ids = [x[0] for x in result]
    patient_ids = [x[1] for x in result]
    roiNames = [x[2] for x in result]
    cur.close()
    for idx, db_id in enumerate(ids):
        cur2=con.cursor()
        cur2.execute('SELECT stdROIName FROM structure_set_roi_sequence_copy WHERE fk_patient_id="'+str(patient_ids[idx])+'" AND ROIName = "'+roiNames[idx]+'"')
        print('SELECT stdROIName FROM structure_set_roi_sequence_copy WHERE fk_patient_id="'+str(patient_ids[idx])+'" AND ROIName = "'+roiNames[idx]+'"')
        r = cur2.fetchall()
        print r
        if r:
            stdROIName = r[0][0]
            cur2.execute('UPDATE contour_sequence SET stdROIName = "'+stdROIName+'" WHERE id="'+str(db_id)+'"')
        print db_id
        con.commit()
        cur.close()
                    
def addHeightWidth():
    con=db.connect('localhost','root','$rt_ds_37','rt_hn')
    cur=con.cursor()
    cur.execute('SELECT id, fk_sop_id FROM ct_image')
    result =  cur.fetchall()
    db_ids = [x[0] for x in result]
    ct_fk_sop_ids = [x[1] for x in result]
    cur.close()

    for idx, db_id in enumerate(db_ids):
        cur2=con.cursor()
        cur2.execute('SELECT Rows, Columns FROM image_plane_pixel WHERE fk_sop_id="'+str(ct_fk_sop_ids[idx])+'"')
        result2=cur2.fetchall()
        width = result2[0][1]
        height = result2[0][0]
        cur2.close()
        cur3=con.cursor()
        cur3.execute('UPDATE ct_image SET width="'+str(width)+'", height="'+str(height)+'" WHERE id="'+str(db_id)+'"')
        con.commit()
        print width, height
        print db_id
        cur3.close()

def writeJSPixelData2():
    fk_patient_id=1
    con = db.connect('localhost','root','$rt_ds_37','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT fk_sop_id, fk_series_id, fk_study_id, fk_patient_id FROM ct_image WHERE fk_patient_id="'+str(fk_patient_id)+'" ORDER BY zIndex ASC')
    con.close()
    tempResultContainer = cur.fetchall()
    ct_fk_sop_ids=[x[0] for x in tempResultContainer]
    ct_fk_series_ids=[x[1] for x in tempResultContainer]
    ct_fk_study_ids=[x[2] for x in tempResultContainer]
    ct_fk_patient_ids=[x[3] for x in tempResultContainer]

    #jsString = ""
    os.makedirs('/home/dsrt/django/dsrt/dsrt/static/jsPixelData/1_1/')   
    for idx, sop_id in enumerate(ct_fk_sop_ids):
        ds=dicom.read_file('/home/dsrt/django/dsrt/dsrt/static/dicom/'+str(ct_fk_patient_ids[idx])+'/'+str(ct_fk_study_ids[idx])+'/'+str(ct_fk_series_ids[idx])+'/'+str(ct_fk_sop_ids[idx])+'.dcm')
        pixelData=ds.pixel_array         
        rows = ds.Rows
        columns = ds.Columns
        pixelData=np.float32(pixelData)
        #pixelDataRescaled=(pixelData/np.amax(pixelData))*255	
        pixelDataRescaled=(pixelData/2177)*255	
        pixelDataFinal=pixelDataRescaled
        pixelDataFinal[np.nonzero(pixelDataFinal>255)]=255
        pixelDataFinal[np.nonzero(pixelDataFinal<0)]=0
        t1=np.reshape(pixelDataFinal,rows*columns,order='C')
        t2=np.repeat(t1,3)
        t3=np.reshape(t2,(rows*columns,3),order='C')
        t4=255*np.ones((rows*columns,1))
        t5=np.concatenate((t3,t4),1)
        t6=np.reshape(t5,rows*columns*4,order='C')
        t6 = [round(x,0) for x in t6]
        jsString = "var pix = " + str(list(t6)) + ";\n consolidateImages1_1(pix,"+str(idx)+");"
        f = open("/home/dsrt/django/dsrt/dsrt/static/jsPixelData/1_1/"+str(idx)+"_1.js","w")
        f.write(jsString)
        f.close()
        print idx

def insertDVH():
    con = db.connect('localhost','root','$rt_ds_37','rt_hn')
    cur = con.cursor()
    cur.execute('SELECT id FROM structure_set_roi_sequence_copy')
    ids = cur.fetchall()
    for db_id in ids:
        db_id = int(db_id[0])
        cur.execute('SELECT stdROIName, dvhDose, dvhVolume FROM structure_set_roi_sequence_copy WHERE id="'+str(db_id)+'"')
        result = cur.fetchall()
        dvhDose = result[0][1]
        dvhVolume = result[0][2]
        dvhDose = dvhDose.lstrip('[').rstrip(']').split(",")
        dvhVolume = dvhVolume.lstrip('[').rstrip(']').split(",")
        dbString = '['
        if (result[0][0][0]=='p' and result[0][0][1]=='t' and result[0][0][2]=='v'):
            dbString=dbString+'[0,'+dvhVolume[0]+'],'
        for idx, doseItem in enumerate(dvhDose):
            dbString = dbString + '[' + str(doseItem) + "," + str(dvhVolume[idx]) + ']'
            if idx!=len(dvhDose)-1:
                dbString = dbString + ","
        print idx
        dbString = dbString + ']'
        cur.execute('UPDATE structure_set_roi_sequence_copy SET dvhCumulative="'+dbString+'" WHERE id="'+str(db_id)+'"')
        con.commit()
        
writeJSPixelData()
