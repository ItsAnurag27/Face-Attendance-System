import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
cred = credentials.Certificate("facedatabase-deb44-firebase-adminsdk-4omkj-6e1acab7bc.json")
firebase_admin.initialize_app(cred,{

    'databaseURL':"https://facedatabase-deb44-default-rtdb.firebaseio.com/",
    'storageBucket': "facedatabase-deb44.appspot.com"
})

bucket = storage.bucket()

# Create a video capture object for your webcam (index 0)
cap = cv2.VideoCapture(0)

# Optionally set the video resolution (if supported by your camera)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Load the background image (replace 'Resources/background.png' with your actual path)
imgBackground = cv2.imread('Resources/background.png')
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList =[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
print(len(imgModeList))

#load encoding file
print("loading encode file..")
file=open('EncodeFile.p','rb')

encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListknown, studentIds = encodeListKnownWithIds
print(studentIds)
print("encode file loaded..")


modeType = 0
counter = 0
id = -1
imgStudent =[]
while True:

    # Capture a frame from the video stream
    success, img = cap.read()
    imgS =cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
    faceCurFrame =face_recognition.face_locations(imgS)
    encodeCurFrame =face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480,55:55 + 640] = img
    imgBackground[44:44+633,808:808 + 414] = imgModeList[modeType]
    if  faceCurFrame:
        for encodeFace,faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches=face_recognition.compare_faces(encodeListknown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListknown,encodeFace)
            # print("maatches",matches)
            # print("facedis",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Mtach index",matchIndex)

            if matches[matchIndex]:

                print("known face detected")
                print(studentIds[matchIndex])

                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)
                id = studentIds[matchIndex]

                if counter ==0:
                    cvzone.putTextRect(imgBackground,"loading",(275,400))
                    cv2.imshow("face attandance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType =1
        if counter!=0:

            if counter ==1:
                #getting data
                studentinfo =db.reference(f'Student/{id}').get()
                print(studentinfo)
                #get the image a/c users
                blob = bucket.get_blob(f'images/{id}.png')
                array=np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #updates users attendance
                datetimeObject = datetime.strptime(studentinfo['last_attendance_time'],
                                            "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed >30:
                    ref = db.reference(f'student/{id}')
                    studentinfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentinfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType !=3:

                if 10<counter<20:
                    modeType = 2
                imgBackground[44:44+633,808:808+414] = imgModeList[modeType]
                if counter<=10:



                    cv2.putText(imgBackground,str(studentinfo['total_attendance']),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground, str(studentinfo['branch']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground,str(id),(1006,493),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)

                    (w,h), _ =cv2.getTextSize(studentinfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground,str(studentinfo['name']),(808+offset,445),
                                cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)
                    imgBackground[175:175+216,909:909+216] = imgStudent




                counter +=1

                if counter >=20:
                    counter =0
                    modeType=0
                    studentinfo=[]
                    imgStudent=[]
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0



        # Example processing (replace with your actual face detection/recognition code)
    #cv2.imshow("webcam", img)
    cv2.imshow("face attandance", imgBackground)# Display the captured f
    cv2.waitKey(1)

# Release the video capture object and close all wi
