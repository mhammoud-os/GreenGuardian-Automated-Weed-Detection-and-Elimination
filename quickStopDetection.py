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
imH = 1100
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
min_conf_threshold = 0.2

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
    sendDataOverSerialPort("1")
    sleep(amount)
    sendDataOverSerialPort("5")
def movebackward(amount):
    sendDataOverSerialPort("3")
    sleep(amount)
    sendDataOverSerialPort("5")

def getPrediction():
    frame = picam2.capture_array()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    return {'boxes':interpreter.get_tensor(output_details[boxes_idx]['index'])[0],'score':interpreter.get_tensor(output_details[scores_idx]['index'])[0]}


sendDataOverSerialPort("1")
while(True):
    prediction = getPrediction();
    
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(prediction['score'])):
        if ((prediction['score'][i] > min_conf_threshold) and (prediction['score'][i] <= 1.0)):
            print("WEED!")
            sendDataOverSerialPort("5")
            moveforward(1)
            sleep(2)

            prediction = getPrediction();
            weedsPos = []
            for i in range(len(prediction['score'])):
                if ((prediction['score'][i] > min_conf_threshold) and (prediction['score'][i] <= 1.0)):
                    move_amount =2*(prediction['boxes'][i][0] + prediction['boxes'][i][2])/2 
                    spray_angle =str(int(1600*(1-(prediction['boxes'][i][1] + prediction['boxes'][i][3])/2)+600))
                    weedsPos.append([spray_angle, move_amount])
            print(weedsPos)
            weedsPos.sort(key=lambda l: l[1])
            print(weedsPos)
            for i in range(len(weedsPos)):
                sendDataOverSerialPort("8")
                for j in weedsPos[i][0]:
                    sendDataOverSerialPort(j)
                sendDataOverSerialPort("q")
                if i != len(weedsPos)-1:
                    weedsPos[i+1][1] -= weedsPos[i][1]
                moveforward(weedsPos[i][1])
                print(weedsPos[i][1])
                print(weedsPos[i][0])

                sendDataOverSerialPort("6")
                print("spraying")
                sleep(1)
                print("endingSpray")
                sendDataOverSerialPort("7")
            print("done")

            moveforward(2)
            sendDataOverSerialPort("1")
            break

            
            
            """

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 4)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
            """

"""
    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
"""
