import os
import json
from os import listdir
from os.path import isfile, join

# reads the input data
path = "file.json"
openFile = open(path, "r")
fileData = json.load(openFile)

# What to Add at the start of the file Names
nameAdd = "gs://cloud-ai-platform-ef85cba5-03a6-46a2-8ac8-2f8fcd138294/"

# This is needed for some reason
ResourceLabels = {"aiplatform.googleapis.com/annotation_set_name": "6974310007122690048"}

# These are the width and height of the images
width = 640
height = 640

newData = []

# This is the format needed
# {"imageGcsUri":"gs://cloud-ai-platform-ef85cba5-03a6-46a2-8ac8-2f8fcd138294/resized011a_jpg.rf.188f0f379bee36325155637889ea7c0e.jpg","boundingBoxAnnotations":[{"displayName":"weed","xMin":0.2315202231520223,"xMax":0.8131101813110181,"yMin":0.17852161785216178,"yMax":0.7782426778242678,"annotationResourceLabels":{"aiplatform.googleapis.com/annotation_set_name":"6974310007122690048"}}],"dataItemResourceLabels":{}}
for i in fileData:
    line = {"imageGcsUri": nameAdd + i["image"], "boundingBoxAnnotations": []}
    for j in i["annotations"]:
        # (x, y) represents the center of the rectangle, and (w, h) are its width and height
        x = j["coordinates"]["x"]
        y = j["coordinates"]["y"]
        w = j["coordinates"]["width"]
        h = j["coordinates"]["height"]
        # (xmin, ymin) and (xMax, yMax) represent the coordinates of the two corners of the rectangle
        xMin = (x - w / 2) / width
        yMin = (y - h / 2) / height
        xMax = (x + w / 2) / width
        yMax = (y + h / 2) / height

        line["boundingBoxAnnotations"].append(
            {"displayName": j["label"], "xMin": xMin, "xMax": xMax, "yMin": yMin, "yMax": yMax,
             "annotationResourceLabels": ResourceLabels})
        line["dataItemResourceLabels"] = {}
    newData.append(line)
for i in newData:
    print(i)

# Writes the file in jsonl format
path = "file.jsonl"
with open(path, "w") as outfile:
    for entry in newData:
        json.dump(entry, outfile)
        outfile.write('\n')
