#https://stackoverflow.com/questions/28327020/opencv-detect-mouse-position-clicking-over-a-picture

import numpy as np 
import cv2

def detect_click(imshow_string, img, cap):

    cap = cv2.VideoCapture(0)

    #This will display all the available mouse click events  
    #events = [i for i in dir(cv2) if 'EVENT' in i]
    #print(events)

    #This variable we use to store the pixel location
    refPt = []

    #click event function
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x,",",y)
            refPt.append([x,y])
            font  = cv2.FONT_HERSHEY_SIMPLEX
            strXY = str(x)+", "+str(y)
            cv2.putText(img, strXY, (x,y), font, 0.5, (255,255,0), 2)
            cv2.imshow("image", img)

        if event == cv2.EVENT_RBUTTONDOWN:
            blue   = img[y, x, 0]
            green  = img[y, x, 1]
            red    = img[y, x, 2]
            font   = cv2.FONT_HERSHEY_SIMPLEX
            strBGR = str(blue)+", "+str(green)+","+str(red)
            cv2.putText(img, strBGR, (x,y), font, 0.5, (0,255,255), 2)
            cv2.imshow("image", img)


    #Here, you need to change the image name and it's path according to your directory
    #img = cv2.imread(r"C:\Users\Charlie\Downloads\psionic_monk.jpg")

    #calling the mouse click event
    #cv2.setMouseCallback("image", click_event)

    while(len(refPt) < 1):#True):
        _, img = cap.read()
        cv2.setMouseCallback("image", click_event)
        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    #cv2.destroyAllWindows()

    return np.array([[refPt[0]]], dtype=np.float32)















#def on_click(event, x, y, p1, p2):
#    if event == cv2.EVENT_LBUTTONDOWN:
#        cv2.circle(lastImage, (x, y), 3, (255, 0, 0), -1)

#cap = cv2.VideoCapture(0)
#while(True): 
#    cv2.namedWindow('image')
#    image = cap.read()
#    #cv2.setMouseCallback('image', on_click)
#    cv2.imshow("mouseclick", image)

#cap.release()
#cv2.destroyAllWindows()

#global mouseX, mouseY

#def draw_circle(event,x,y,flags,param):
#    if event == cv2.EVENT_LBUTTONDBLCLK:
#        cv2.circle(img,(x,y),100,(255,0,0),-1)
#        mouseX,mouseY = x,y

#img = np.zeros((512,512,3), np.uint8)
#cv2.namedWindow('image')
#cv2.setMouseCallback('image',draw_circle)

#while(1):
#    cv2.imshow('image',img)
#    if event == cv2.EVENT_LBUTTONDBLCLK:
#        print(event)
#    k = cv2.waitKey(20) & 0xFF
#    if k == 27:
#        break
#    elif k == ord('a'):
#        print(mouseX, mouseY)
