#import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

Motor1A = 29
Motor1B = 31
 
Motor2A = 16
Motor2B = 18

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)

GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)

def sol():
    GPIO.output(Motor1A,GPIO.HIGH)
    GPIO.output(Motor1B,GPIO.LOW)
    return

def on():
    GPIO.output(Motor2A,GPIO.HIGH)
    GPIO.output(Motor2B,GPIO.LOW)
    return

def sag():
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.HIGH)
    return

def arka():
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.HIGH)
    return

def orta():
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.LOW)
    return

def dur():
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.LOW)
    return

sleep(10)

print(cv2.__version__)
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (160, 128)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(160, 128))

# allow the camera to warmup
#time.sleep(0.1)
# capture frames from the camera
for frames in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frames.array
	crop = image[60:128, 0:160]
	gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (5,5), 0)
	ret,thresh = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)
	ret,contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)
	# show the frame
	
	if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            cx = 0
            cy = 0
            if((not(M['m10']==0 and M['m00']==0))or (not(M['m01']==0 and M['m00']==0))):
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
            else:
                print("sifir/sifir engellendi")
 
            cv2.line(crop,(cx,0),(cx,720),(255,0,0),1)
            cv2.line(crop,(0,cy),(1280,cy),(255,0,0),1)
 
            cv2.drawContours(crop, contours, -1, (0,255,0), 1)
            
            if cx >= 120:
                sag()
                on()
                print("sag")
            elif (cx < 120 and cx > 81) or (cx>40 and cx<79):
                orta()
                on()
                print("orta")
            elif cx <= 40:
                sol()
                on()
                print("sol")
            else:
                orta()
                print("dur")
	cv2.imshow("Frame", crop)
	key = cv2.waitKey(1)
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	
	# if the `q` key was pressed, break from the loop
	if cv2.waitKey(1) == ord("q"):
		break
GPIO.cleanup()