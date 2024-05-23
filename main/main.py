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

# HMC5883L Program taken from: 
#https://how2electronics.com/interfacing-hmc5883l-magnetometer-with-raspberry-pi/
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

MODEL_NAME = 'model1'
GRAPH_NAME = 'detect.tflite'
LABELMAP_NAME = 'labelmap.txt'
min_conf_threshold = 0.25

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter

print("Start")

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])


print("Start")
interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()
print("Start")

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Check output layer name to determine if this model was created with TF2 or TF1,
# because outputs are ordered differently for TF2 and TF1 models
outname = output_details[0]['name']

if ('StatefulPartitionedCall' in outname): # This is a TF2 model
    boxes_idx, classes_idx, scores_idx = 1, 3, 0
else: # This is a TF1 model
    boxes_idx, classes_idx, scores_idx = 0, 1, 2

def moveforward(amount):
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
    frame_resized = cv2.resize(frame_rgb, (width, height))

    avg_color_per_row = np.average(frame_resized, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    print(f"color: {avg_color[2]:.2f}, {avg_color[1]:.2f}, {avg_color[0]:.2f}")
    if not (avg_color[1]>avg_color[0]+0 and avg_color[1]>avg_color[2]+0 and avg_color[1] > 90):
        print(f"not green: {avg_color[2]:.2f}, {avg_color[1]:.2f}, {avg_color[0]:.2f}")
        return True

    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    return {'boxes':interpreter.get_tensor(output_details[boxes_idx]['index'])[0],'score':interpreter.get_tensor(output_details[scores_idx]['index'])[0]}

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
            
    prediction = getPrediction();
    if prediction == True:
        print("Camera Turn")
        sendDataOverSerialPort("3")
        sleep(1.7)
        turn()
        continue
    
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(prediction['score'])):
        if ((prediction['score'][i] > min_conf_threshold) and (prediction['score'][i] <= 1.0)):
            print("WEED!")
            sendDataOverSerialPort("5")
            sleep(0.5)

            prediction = getPrediction();
            if prediction == True:
                continue
            weedsPos = []
            for i in range(len(prediction['score'])):
                if ((prediction['score'][i] > min_conf_threshold) and (prediction['score'][i] <= 1.0)):
                    move_amount =(prediction['boxes'][i][0] + prediction['boxes'][i][2])/2 * 5

                    spray_angle =str(int(1700*(1-(prediction['boxes'][i][1] + prediction['boxes'][i][3])/2)+600))
                #spray_angle =str(int(7600*(1-(prediction['boxes'][i][1] + prediction['boxes'][i][3])/2)+600))
                    weedsPos.append([spray_angle, move_amount])
            print(weedsPos)
            weedsPos.sort(key=lambda l: l[1])
            print(weedsPos)
            for i in range(len(weedsPos)):
                sleep(1)
                sendDataOverSerialPort("8")
                sendNum(weedsPos[i][0])

                sendDataOverSerialPort("q")
                sleep(1)
                if i != len(weedsPos)-1:
                    weedsPos[i+1][1] -= weedsPos[i][1]
                moveforward(weedsPos[i][1]*8)
                print(weedsPos[i][1])
                print(weedsPos[i][0])

                sendDataOverSerialPort("6")
                print("spraying")
                sleep(1)
                print("endingSpray")
                sendDataOverSerialPort("7")
                sleep(0.05)
                sendDataOverSerialPort("4")
            print("done")

            if len(weedsPos)>0:
                print("HI")
                moveforward(8)
            sleep(0.1)

            serial.Serial('/dev/ttyACM0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False).close()
            sleep(0.2)
            ser = serial.Serial('/dev/ttyACM0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) 
            sendDataOverSerialPort("4")
            sleep(0.1)
            sendDataOverSerialPort("1")
            break

