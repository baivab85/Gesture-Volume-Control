import cv2
import time
import numpy as np
import mediapipe as mp
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands)
        self.hands.detection_confidence = detectionCon
        self.hands.tracking_confidence = trackCon
        
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
#                     self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
                      self.drawSpec = self.mpDraw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=4)
                      self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS, landmark_drawing_spec=self.drawSpec)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                              (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
    
        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    def main(self):
        pTime = 0
        cap = cv2.VideoCapture(1)
        

wCam, hCam = 500, 700

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
ptime = 0
detector = handDetector(detectionCon=0.7, trackCon=0.1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()
minvol=volRange[0]
maxvol=volRange[1]
vol=0
volVB=400
volPer=0
while True:
    success, img = cap.read()
    

    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)
    

#     if lmlist:
#         for item in lmlist:
#             if len(item) > 0 and item[0][0] == 2:
#                 print(item)
#     for item in lmlist[0]:
#        if item[0] == 4:
#            cv2.circle(img, (item[1], item[2]), 15, (255, 0, 255), cv2.FILLED)
#        if item[0] == 8:
#            cv2.circle(img, (item[1], item[2]), 15, (255, 0, 255), cv2.FILLED)
     # Assuming you have detected the landmarks for the forefinger (id=4) and thumb (id=8)
    # Assuming you have detected the landmarks for the forefinger (id=4) and thumb (id=8)
    if lmlist and len(lmlist) > 0 and len(lmlist[0]) > 8:
       x1, y1 = lmlist[0][4][1], lmlist[0][4][2]
       x2, y2 = lmlist[0][8][1], lmlist[0][8][2]
       cx, cy= (x1+x2)//2, (y1+y2)//2

    # Draw circles at the landmarks
       cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
       cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)

    # Draw a line between the two circles
       cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
       cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
       
       length = math.hypot(x2-x1,y2-y2)
       print(length)
        
       vol=np.interp(length,[10,110],[minvol,maxvol])
       volVB=np.interp(length,[10,110],[400,150])
       volPer=np.interp(length,[10,110],[0,100])
      
       print(length,vol)
       volume.SetMasterVolumeLevel(vol, None)
        
       if length<40:
           cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
        
      
    cv2.rectangle(img,(50,150),(85,400),(0,255,0),3)
    cv2.rectangle(img,(50,int(volVB)),(85,400),(0,255,0),cv2.FILLED)
    cv2.putText(img, f':{int(volPer)}%', (40, 440), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    
    cTime = time.time()
    fps = 1 / (cTime - ptime)
    ptime = cTime
    
    cv2.putText(img, f'FPS:{int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    if not success:
        print("Error reading frame from the camera.")
        break

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' key to exit
        break

cap.release()
cv2.destroyAllWindows()


