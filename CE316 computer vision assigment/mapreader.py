#!/usr/bin/env python3


#setupcode:(import, debug, open)line 14-45
#functions:(function[keyword/s]) line 46-103
#task1:(thresholding) line 104-144
#task2:(crop, rotate, triangel) line 145-202
#task3:(tip, postion)line 203-237
#task4:(bearing, postion)line 238-287
#full list of citations()line 289-297

#setup code 
#import our libraries(import).
import sys, math, os 
import cv2 as cv  
import numpy as np

#set debug as false(debug). 
debug = False

# Ensure we were invoked with a single argument(debug).
if len (sys.argv) == 3:
   debug = True
elif len (sys.argv) == 1:
   print ("Usage: %s <image-file>" % sys.argv[0], file=sys.stderr)
   exit (1)

#creat folder "images" to add all outcomes to (debug).
if debug:
   os.system('mkdir images')
   print ("debugmode on") 
else: 
   print ("debugmode off , add third argument on command for debug mode ")
#code to print postion and bearing was moved to the end of the code(postion)(bearing).  

#folder path(debug). 
path = 'images'

#read image(open).
im = cv.imread(sys.argv[1])
 
#functions. 
#creat function to rotate image(function[rotate]). 
#refrence: point, OpenCV, and Alex Rodrigues. "Opencv Python Rotate Image By X Degrees Around Specific Point". Stack Overflow, 2022, https://stackoverflow.com/questions/9041681/opencv-python-rotate-image-by-x-degrees-around-specific-point.
def rotate(image, angle, center = None, scale = 1.0):
    (h, w) = image.shape[:2]
    if center is None:
        center = (w / 2, h / 2)
    M = cv.getRotationMatrix2D(center, angle, scale)
    rotated = cv.warpAffine(image, M, (w, h))
    return rotated
    
#function to get approximet(function[tip]).
#"Opencv: Contour Features". Docs.Opencv.Org, 2022, https://docs.opencv.org/master/dd/d49/tutorial_py_contour_features.html.
def apr (count , num):
  arc = num*cv.arcLength(count,True)
  approx = cv.approxPolyDP(count,arc,True)
  return approx 


#thresholding and finding contours function(function[thresholding]).
#refrence:using lab 3
def cntr (file):
   grey = cv.cvtColor (file, cv.COLOR_BGR2GRAY)
   blur = cv.GaussianBlur (grey, (5, 5), 0)
   t, binary = cv.threshold (blur, 0 , 255, cv.THRESH_BINARY+cv.THRESH_OTSU)                              
   contrs, junk = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) 
   return contrs 
   
#function to draw the point on the tip of the pointer(function[tip]). 
def drawp (i,image):
   cv.putText (image, "pointer here", (approx[i][0][0]-200, approx[i][0][1]), cv.FONT_HERSHEY_SIMPLEX, 1, 0, 3, cv.LINE_AA)
   mp3 = cv.circle(image, (approx[i][0][0],approx[i][0][1]), radius=0, color= 0, thickness=11)
   cv.putText (image, "pointer here", (approx[i][0][0]-200, approx[i][0][1]), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 190, 255), 1, cv.LINE_AA)
   mp3 = cv.circle(image, (approx[i][0][0],approx[i][0][1]), radius=0, color=(0, 190, 255), thickness=7)
   tip = approx[i][0]
   return tip 
   
#function to calculate distance from point to point(function[tip]).
#refrence:"How To Find Distance Between Two Coordinates In Python Code Example". Codegrepper.Com, 2022, https://www.codegrepper.com/code-examples/python/how+to+find+distance+between+two+coordinates+in+python. 
def calcdis(x1,y1,x2,y2):
   dist = math.sqrt((x2-x1)**2 + (y2 - y1)**2)
   return dist

# find midpoint between 2 other point(function[bearing]).  
def midpoint (cord1, cord2):
   point = (int((cord1[0]+cord2[0])/2), int((cord1[1]+cord2[1])/2)) 
   return point 
   
#function to find the bearing(function[bearing]).
#"Find The Angle Between Three Points From 2D Using Python". Medium, 2022, https://manivannan-ai.medium.com/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd.
def fa(p1,p2,p3):
   ang = math.degrees(math.atan2(p3[1]-p2[1],p3[0]-p2[0])- math.atan2(p1[1]-p2[1],p1[0]-p2[0]))
   return 360 - ang if ang < 0 else ang  
#end of functions. 
  
#task1 
#convert colours to hsv and set diffrent masks and creat difrrent copies of the image with diffrent masks removed for other purposes(thresholding).    
hue = cv.cvtColor(im, cv.COLOR_BGR2HSV)

mask = cv.inRange(hue, (0,0,30), (180, 159,255)) # this mask removes as much blue as possible even if other colours are removed 
mask2 = cv.inRange(hue, (0,0,30), (180, 185,255))# this mask removes blue colour but with minmising the risk of other colours being removed 


mp0 = cv.bitwise_and (im,im, mask= mask) #used to seprate as much blue as possible and find contours for map to rotate then find its contours again to crop (task 1) 
mp1 = cv.bitwise_and (im,im, mask= mask2) #used to seperate the red pointer from the map after we crop in order to find its contours to segment it (task2)
mp2 = cv.bitwise_and (im,im, mask= mask2) #draw the triangel contours on the map (task2/3)
mp3 = cv.bitwise_and (im,im, mask= mask2)#draw the lines between pointer tip to mid point and mid point to top point , then we find the angel  

if debug: 
   cv.imshow("inrange map", mp0)
   cv.waitKey (0)
   cv.imwrite(os.path.join(path, "inrangemap.png"), mp0)



# grayscale thresholding on image before removing background (thresholding).
contours = cntr (im )                                     
cv.drawContours (im, contours, -1, (0, 0, 255), 2) 

if debug:
   cv.imshow("thres w out inrange map", im)
   cv.waitKey (0)
   cv.imwrite(os.path.join(path, "thres w out inrange map.png"), im)  

# grayscale thresholding on image after removing background (thresholding).
contours1 = cntr (mp0)                                                                                                          
cv.drawContours (mp0, contours1, -1, (0, 0, 255), 1) 

if debug: 
   cv.imshow("thres w  inrange map", mp0)
   cv.waitKey (0) 
   cv.imwrite(os.path.join(path, "theres w inrange map.png"), mp0)  
#end of task1.

#task2.
#we set 2 diffrent masks to remove the background.  ps: this in range function works better for the pointer which is why it was changed.(triangel).
#refrence: OpenCV, Finding. "Finding Red Color In Image Using Python & Opencv". Stack Overflow, 2022, https://stackoverflow.com/questions/30331944/finding-red-color-in-image-using-python-opencv.  
red1 = np.array([0,50,50])
red2 = np.array([20,255,255])
mask3=cv.inRange(hue,red1,red2)
red3 = np.array([170,50,50])
red4 = np.array([190,255,255])
mask4=cv.inRange(hue,red3,red4)
mask34 = mask3+mask4
mp1[np.where(mask34==0)]=0

#set the values to find the rotated image (rotate).
#"Opencv: Contour Features". Docs.Opencv.Org, 2022, https://docs.opencv.org/master/dd/d49/tutorial_py_contour_features.html.  
cnt = contours1[0]
rect = cv.minAreaRect(cnt)
box = cv.boxPoints(rect)
box = np.int0(box)
cv.drawContours(mp0,[box],0,(255,0,0),1)
ang = rect[2] 

#rotates all images and copies(rotate).
im = rotate(im, ang)
mp0 = rotate(mp0, ang)
mp1 = rotate(mp1, ang)  
mp2 = rotate(mp2, ang)
mp3 = rotate(mp3, ang)



#find contours needed to crop (crop).
#refrence "How To Crop An Object In An Image In Python Using Opencv". Learningaboutelectronics.Com, 2022, http://www.learningaboutelectronics.com/Articles/How-to-crop-an-object-in-an-image-in-Python-OpenCV.php. 
contours0= cntr (mp0)
sorted_contours=sorted(contours0,key=cv.contourArea,reverse=True)                                       
for (i,c) in enumerate(sorted_contours): 
     x,y,w,h= cv.boundingRect(c)
      
#crop images(crop). 
mp1= mp1[y:y+h, x:x+w]
mp2 = mp2[y:y+h, x:x+w]
mp3 = mp3[y:y+h, x:x+w]
if debug:
   cv.imshow('tri',mp1 ) 
   cv.waitKey (0) 
   cv.imwrite(os.path.join(path, "tri.png"), mp1) 
   
#find contours on map(triangel).    
contours2= cntr (mp1)
cv.drawContours (mp2, contours2, -1, (255, 255, 255), 2)

if debug:
   cv.imshow('tri map ',mp2 ) 
   cv.waitKey (0)
   cv.imwrite(os.path.join(path, "tri map.png"), mp2) 
#end of task2. 

#task3. 
#find approximite which find the edges of the triangle(tip).
cnt = contours2[0]
approx = apr(cnt, 0.1)

#find distance between points(tip).
out1 = calcdis(approx[0][0][0] , approx[0][0][1] , approx[1][0][0] , approx[1][0][1])
out2 = calcdis(approx[0][0][0] , approx[0][0][1] , approx[2][0][0] , approx[2][0][1])
out3 = calcdis(approx[2][0][0] , approx[2][0][1] , approx[1][0][0] , approx[1][0][1])

   
#if statment where the common point in the 2 longest distances = the tip of pointer(tip).  
if (out1 > out3) & (out2 > out3):
   tip=drawp(0,mp3)
   crd1 = approx [1][0]
   crd2 = approx [2][0]
elif (out1 > out2) & (out3 > out2):
   tip=drawp(1,mp3)
   crd1 = approx [2][0]
   crd2 = approx [0][0]
else:
   tip=drawp(2,mp3)
   crd1 = approx [1][0]
   crd2 = approx [0][0] 
if debug:
   cv.imshow('pointer',mp3 )
   cv.waitKey (0)
   cv.imwrite(os.path.join(path, "pointer.png"), mp3) 
    
#image postion(postion).            
postion = [((tip[1]/mp3.shape[0])),(((mp3.shape[1]-tip[0])/mp3.shape[1]))]
#end of task3.

#task4.
#find the mid point and draw it on image(bearing).
midP = midpoint(crd1, crd2)
mp3 = cv.circle(mp3, (midP[0],midP[1]), radius=0, color= 0, thickness=11)
mp3 = cv.circle(mp3, (midP[0],midP[1]), radius=0, color= (255,255,255), thickness=7)

if debug:
   cv.imshow('midpoint',mp3 )
   cv.waitKey (0)
   cv.imwrite(os.path.join(path, "midpoint.png"), mp3)  
   
#draw line between tip and mid point and midpoint and top  of the map(bearing).

   mp3 = cv.line(mp3, (tip[0],tip[1]), (midP), (0,0,0), thickness=7)
   mp3 = cv.line(mp3, (midP), (midP[0],0), (0, 0, 0), thickness=7)
   mp3 = cv.line(mp3, (tip[0],tip[1]), (midP), (0, 190, 255), thickness=4)
   mp3 = cv.line(mp3, (midP), (midP[0],0), (255,255,255), thickness=4) 
   
#top point value (bearing). 
topP = (midP[0], 0)


#find bearing and transform the angel from 360 to zero(bearing).   
bearing = fa(tip,midP,topP) 

if bearing >= 360: 
  bearing = bearing - 360
  
#print the angel text on image(bearing).  
txt2= ("%.1f %s" % (int(bearing), "degrees"))
cv.putText (mp3, txt2 , (midP[0]-80, midP[1]+40), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv.LINE_AA)
cv.putText (mp3, txt2 , (midP[0]-80, midP[1]+40), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv.LINE_AA)

#assign postion bearing and then print the file name and our values(postion)(bearing).
print ("The filename to work on is %s." % sys.argv[1])
xpos = postion[0]
ypos = postion[1]
hdg = bearing 

#Output the position and bearing in the form required by the test harness(postion)(bearing).
print ("POSITION %.3f %.3f" % (xpos, ypos))
print ("BEARING %.2f" % hdg)
if debug:
   cv.imshow('final picture',mp3 )
   cv.waitKey (0)
   cv.imwrite(os.path.join(path, "angel.png"), mp3) 
#end of task4.

#full list of citations 
#"How To Crop An Object In An Image In Python Using Opencv". Learningaboutelectronics.Com, 2022, http://www.learningaboutelectronics.com/Articles/How-to-crop-an-object-in-an-image-in-Python-OpenCV.php.
#OpenCV, Finding. "Finding Red Color In Image Using Python & Opencv". Stack Overflow, 2022, https://stackoverflow.com/questions/30331944/finding-red-color-in-image-using-python-opencv.
#"Opencv: Contour Features". Docs.Opencv.Org, 2022, https://docs.opencv.org/master/dd/d49/tutorial_py_contour_features.html.
#"How To Find Distance Between Two Coordinates In Python Code Example". Codegrepper.Com, 2022, https://www.codegrepper.com/code-examples/python/how+to+find+distance+between+two+coordinates+in+python.
#"Find The Angle Between Three Points From 2D Using Python". Medium, 2022, https://manivannan-ai.medium.com/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd.
#point, OpenCV, and Alex Rodrigues. "Opencv Python Rotate Image By X Degrees Around Specific Point". Stack Overflow, 2022, https://stackoverflow.com/questions/9041681/opencv-python-rotate-image-by-x-degrees-around-specific-point.
