#This program stops when a weed is identified
#it writest the image to a file using picam2 and them reads the file to identifie if there is a weed
#it is very slow processing 1 frame per secound
import os
import argparse
import cv2
import numpy as np
import sys
import importlib.util
import serial
from picamera2 import Picamera2, Preview
import time
from time import sleep
import smbus
import math

# HMC5883L register addresses
ADDRESS = 0x1E
CONFIG_A = 0x00
CONFIG_B = 0x01
MODE = 0x02
X_MSB = 0x03
Z_MSB = 0x05
Y_MSB = 0x07
 
bus = smbus.SMBus(1)
sleep(1)
 
def setup():
    bus.write_byte_data(ADDRESS, CONFIG_A, 0x70)  # Set to 8 samples @ 15Hz
    bus.write_byte_data(ADDRESS, CONFIG_B, 0x20)  # 1.3 gain LSb / Gauss 1090 (default)
    bus.write_byte_data(ADDRESS, MODE, 0x00)  # Continuous measurement mode 
 
def read_raw_data(addr):
    # Read raw 16-bit value
    high = bus.read_byte_data(ADDRESS, addr)
    low = bus.read_byte_data(ADDRESS, addr+1)
    
    # Combine them to get a 16-bit value
    value = (high << 8) + low
    if value > 32768:  # Adjust for 2's complement
        value = value - 65536
    return value
 
def compute_heading(x, y):
    # Calculate heading in radians
    heading_rad = math.atan2(y, x)
    
    # Adjust for declination angle (e.g. 0.22 for ~13 degrees)
    declination_angle = 0.22
    heading_rad += declination_angle

    # Correct for when signs are reversed.
    if heading_rad < 0:
        heading_rad += 2 * math.pi

    # Check for wrap due to addition of declination.
    if heading_rad > 2 * math.pi:
        heading_rad -= 2 * math.pi
 
    # Convert radians to degrees for readability.
    heading_deg = heading_rad * (180.0 / math.pi)
    
    return heading_deg

setup()
"""
       x = read_raw_data(X_MSB)
       y = read_raw_data(Y_MSB)
       heading = compute_heading(x, y)
       print(f"X: {x} uT, Y: {y} uT, Heading: {heading:.2f}")
       time.sleep(0.01)
"""

#bus
ser = serial.Serial('/dev/ttyACM0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) 
ser.flushInput()
ser.flushOutput()

#serial.Serial('/dev/ttyACM0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False).close()
def sendDataOverSerialPort(data):
    ser = serial.Serial(port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1)

    if ser.isOpen():
        try:
            ser.flushInput()
            ser.flushOutput()
            ser.write(bytes(data,'iso-8859-1'))
        except Exception as e1:
            logMsg ='[serialPrinter]: Communication error...:' + str(e1)
            print(logMsg)    



sendDataOverSerialPort("5")

imW = 2304 
imH = 700
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"format": 'XRGB8888', "size": (imW, imH)}, lores={"size": (imW, imH)}, display="lores")

picam2.configure(camera_config)
#picam2.start_preview(Preview.QTGL)
picam2.start()
print("Start")
time.sleep(0.5)

def moveforward(amount):
    amount = int(amount)
    if amount <=2:
        return
    sendDataOverSerialPort("m")
    sendNum(amount)
    sendDataOverSerialPort("q")

def turn_right(new_heading):
    print("new_heading" + str(new_heading))
    sleep(0.5)
    sendDataOverSerialPort("2")
    sendDataOverSerialPort("l")
    sendNum(0)
    sendDataOverSerialPort("q")
    sleep(0.01)
    sendDataOverSerialPort("r")
    sendNum(30000)
    sendDataOverSerialPort("q")
    sendDataOverSerialPort("1")
    while True:
        x = read_raw_data(X_MSB)
        z = read_raw_data(Z_MSB)
        y = read_raw_data(Y_MSB)
        heading = round(compute_heading(x, y), 2)
        print("turnr" + str(heading))
        if heading + 3 >= new_heading and heading -3 <= new_heading:
            sendDataOverSerialPort("4")
            sendDataOverSerialPort("1")
            sendDataOverSerialPort("r")
            sendNum(0)
            sendDataOverSerialPort("q")
            sendDataOverSerialPort("l")
            sendNum(0)
            sendDataOverSerialPort("q")
            return
        sleep(0.07)
def turn_left(new_heading):
    print("new_heading" + str(new_heading))
    sleep(0.5)
    sendDataOverSerialPort("0")
    sendDataOverSerialPort("l")
    sendNum(30000)
    sendDataOverSerialPort("q")
    sleep(0.01)
    sendDataOverSerialPort("r")
    sendNum(0)
    sendDataOverSerialPort("q")
    sendDataOverSerialPort("1")
    while True:
        x = read_raw_data(X_MSB)
        z = read_raw_data(Z_MSB)
        y = read_raw_data(Y_MSB)
        heading = round(compute_heading(x, y), 2)
        print("turnl" + str(heading))

        if heading + 3 >= new_heading and heading -3 <= new_heading:
            sendDataOverSerialPort("4")
            sendDataOverSerialPort("1")
            sendDataOverSerialPort("r")
            sendNum(0)
            sendDataOverSerialPort("q")
            sendDataOverSerialPort("l")
            sendNum(0)
            sendDataOverSerialPort("q")
            return
        sleep(0.07)
    
def move_right_forward(amount):
    if amount <=2:
        return
    sendDataOverSerialPort("k")
    sendNum(amount)
    sendDataOverSerialPort("q")

    sendDataOverSerialPort("l")
    sendNum(left_motor_speed)
    sendDataOverSerialPort("q")

    sendDataOverSerialPort("r")
    sendNum(right_motor_speed)
    sendDataOverSerialPort("q")
    
def move_left_forward(amount):
    if amount <=2:
        return
    sendDataOverSerialPort("e")
    sendNum(amount)
    sendDataOverSerialPort("q")

    sendDataOverSerialPort("l")
    sendNum(left_motor_speed)
    sendDataOverSerialPort("q")
    sendDataOverSerialPort("r")
    sendNum(right_motor_speed) 
    sendDataOverSerialPort("q")
"""
def movebackward(amount):
    sendDataOverSerialPort("3")
    sleep(amount)
    sendDataOverSerialPort("5")

"""

def sendNum(num):
    num = int(num)
    if num < 0: 
        num = 0
    if num > 20000:
        num =  30000
    for j in str(num):
        sendDataOverSerialPort(j)
        sleep(0.05)

def getPrediction():
    frame = picam2.capture_array()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #frame_resized = cv2.resize(frame_rgb, (width, height))

    avg_color_per_row = np.average(frame_rgb, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    print(f"color: {avg_color[2]:.2f}, {avg_color[1]:.2f}, {avg_color[0]:.2f}")
    if not (avg_color[1]>avg_color[0]+0 and avg_color[1]>avg_color[2]+0 and avg_color[1] > 90):
        print(f"not green: {avg_color[2]:.2f}, {avg_color[1]:.2f}, {avg_color[0]:.2f}")
        return True


    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower and upper limits for the yellow color
    lower_limit = np.array([26, 160, 212])
    upper_limit = np.array([30, 247, 255])

    # create a mask for the specified color range
    mask = cv2.inRange(hsv_image, lower_limit, upper_limit)
    # get the bounding box from the mask image
    bbox = cv2.boundingRect(mask)

    if bbox is not None:
        x, y, w, h = bbox
        if x == 0 and y == 0 and w == 0 and h == 0: 
            return False

        return [x/imW, y/imH, (w+x)/imW, (h+y)/imH]
        
    else:
        return False 

    #return {'boxes':interpreter.get_tensor(output_details[boxes_idx]['index'])[0],'score':interpreter.get_tensor(output_details[scores_idx]['index'])[0]}

sendDataOverSerialPort("1")
counter = 0
switch = 0


x = read_raw_data(X_MSB)
y = read_raw_data(Y_MSB)
z = read_raw_data(Y_MSB)
heading = round(compute_heading(x, y), 2)
forward_heading = round(heading, 2)
print("forward Heading" + str(forward_heading) + "......" + str(heading))
turning_speed = 3000

left_motor_speed = 0
right_motor_speed = 0

def turn():
    global switch, forward_heading
    sendDataOverSerialPort("5")
    forward_heading =(forward_heading+180)%360
    if switch == 0:
        sendDataOverSerialPort("2")
        switch = 1
        sleep(0.5)
        #move_right_forward(400)
        turn_right(forward_heading)

    else: 
        sendDataOverSerialPort("0")
        switch = 0
        sleep(0.5)
        turn_left(forward_heading)
        #move_left_forward(400)
    sleep(1)
    sendDataOverSerialPort("4")
    sleep(0.5)
    sendDataOverSerialPort("1")
    sleep(0.5)

while(True):
    sleep(0.1)
    x = read_raw_data(X_MSB)
    z = read_raw_data(Z_MSB)
    y = read_raw_data(Y_MSB)
    heading = round(compute_heading(x, y), 2)
    print("heading" + str(heading) + "  Forward Heading" + str(forward_heading))

    if heading < forward_heading:
        right_motor_speed+= turning_speed
        left_motor_speed-= turning_speed
    else:
        left_motor_speed += turning_speed
        right_motor_speed -= turning_speed
    if heading + 2 >= forward_heading and heading -2 <= forward_heading:
        print("NOOOO")
        left_motor_speed = 0
        right_motor_speed = 0


    counter +=1
    if counter == 6:
        sendDataOverSerialPort("l")
        sendNum(left_motor_speed)
        sendDataOverSerialPort("q")
        sleep(0.01)
        sendDataOverSerialPort("r")
        sendNum(right_motor_speed)
        sendDataOverSerialPort("q")

        counter = 0
        sendDataOverSerialPort("f")
        time.sleep(0.08)
        data_raw = ser.readline()
        data = str(data_raw, 'UTF-8')
        num =""
        for i in data:
            if i.isdigit():
                num+=i
        print(num)
        if len(num) == 0:
            num = 0
        else:
            num = int(num)
        if num <= 48 and num != 0:
            print("Obsticle Turn")
            if num <=20:
                sendDataOverSerialPort("3")
                sleep(0.8)
            turn()
            
    prediction = getPrediction()
    if prediction == True:
        print("Camera Turn")
        sendDataOverSerialPort("3")
        sleep(1.7)
        turn()
        continue

    sleep(0.1)
    if prediction != False:
        print("Weed")
        
        sendDataOverSerialPort("5")

        """
        sleep(1)
        prediction = getPrediction()
        if prediction == True or prediction == False:
            continue
        print("Weed!!!!")
        """
        
        move_amount =(prediction[0] + prediction[2])/2 * 20
        sendDataOverSerialPort("4")

        spray_angle =str(int(1700*(1-(prediction[1] + prediction[3])/2)+600))
        print("weed1")

        sendDataOverSerialPort("8")
        sendNum(spray_angle)
        sleep(0.1)

        sendDataOverSerialPort("q")
        sleep(0.5)
        sendDataOverSerialPort("4")

        moveforward(move_amount)
        print("move", move_amount)

        sleep(0.1)
        sendDataOverSerialPort("6")
        print("spraying")
        sleep(1)
        print("endingSpray")
        sendDataOverSerialPort("7")
        sleep(0.05)
        sendDataOverSerialPort("4")

        #serial.Serial('/dev/ttyACM0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False).close()
        sleep(0.2)
        #ser = serial.Serial('/dev/ttyACM0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) 

        moveforward(8)
        sleep(0.1)

        sendDataOverSerialPort("4")
        sleep(0.1)
        sendDataOverSerialPort("1")
        

