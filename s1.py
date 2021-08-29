import sys
from sys import platform
import os
from os import truncate
import numpy as np
import cv2
import socket
import threading
import time
from threading import Timer
import argparse
import imutils
import glob
import random
import math

def cal_ang(p1, p2, p3):
    # if p1[0]==0 or p1[1]==0 or p2[0]==0 or p2[1]==0 or p3[0]==0 or p3[1]==0:
    #     return -1

    vector1 = [p1[0]-p2[0], p1[1]-p2[1]] #8-11
    vector2 = [p3[0]-p2[0], p3[1]-p2[1]] #8-14
    angle = math.atan2(vector2[1], vector2[0]) - math.atan2(vector1[1], vector1[0])
    angle = angle/math.pi*180 #change arc to degree
    #if angle < 0:
    #    angle= angle + 360
    return angle

#client連進來後會在這
def classfly(client_executor, addr):
    print("welcome to classfy")
    print('Accept new connection from %s:%s...' % addr)
    #try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../python/openpose/Release')
            #os.environ['PATH'] = os.environ['PATH'] + ';' + \
            #    dir_path + '/../../x64/Release;' + dir_path + '/../../bin;'
            os.add_dll_directory(dir_path + '/../../x64/Release')
            os.add_dll_directory(dir_path + '/../../bin')

            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python')
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg",
                        help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../../models/"
    params["net_resolution"] = "256x320"

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1:
            next_item = args[1][i+1]
        else:
            next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-', '')
            if key not in params:
                params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-', '')
            if key not in params:
                params[key] = next_item

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose

    #opWrapper = op.WrapperPython(op.ThreadManagerMode.Synchronous)
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    # opWrapper.execute()
    
    datum = op.Datum()
    cap = cv2.VideoCapture(0)

    count = "0"
    start = int(time.time())
    temp = 0
    text = ""
    uans = "a"
    cans = "a"
    flag = 7
    num = "0"
    user = 0
    while True:
        
        ret, frame = cap.read()
        if ret == False:
            print("erro")
        img = frame
        datum.cvInputData = img

        opWrapper.emplaceAndPop([datum])
        # print(str(datum.poseKeypoints))

        frame = datum.cvOutputData

        if(str(datum.poseKeypoints) == "2.0" or str(datum.poseKeypoints) == "0.0"): #無偵測到人
            continue
        else:
            ans = 0
            temp = int(time.time())
            if temp == start + 30:
                start = temp
            # if temp <= 8:
            #     temp += 1
            # else:
            #     temp = 0

            # if temp == start + 2: #s
            #     ans = random.randint(1,3)  
            
            
            #print(temp)
            if temp <= start + 5:
                count = "1"
                flag = "7"
                uans = "a"
                text = cans + " " + uans + " " + count +" " + flag
                print("1" + text)
                client_executor.send(text.encode('utf-8'))
            elif temp <= start + 7:
                count = "2"
                flag = "7"
                uans = "a"
                text = cans + " " + uans + " " + count +" " + flag
                print("2" + text)
                client_executor.send(text.encode('utf-8'))
            elif temp <= start + 9:
                count = "3"
                flag = "7"
                uans = "a"
                text = cans + " " + uans + " " + count +" " + flag
                print("3" + text)
                client_executor.send(text.encode('utf-8'))
                
            elif temp <= start + 13:
                print("4")
                if temp == start + 10:
                    ans = random.randint(1,3)
                ang = cal_ang(datum.poseKeypoints[0][11], datum.poseKeypoints[0][8], datum.poseKeypoints[0][14])
                if ang >= 0:
                    uans = "usc"
                    user = 1
                elif ang >= -5:
                    uans = "ust"
                    user = 2
                elif ang <= -29:
                    uans = "up"
                    user = 3
                else:
                    uans = " "
                    user = 0

                if ans == 1:
                    if user == 1:
                        flag = "0"
                    elif user == 2:
                        flag = "2"
                    else:
                        flag = "1"
                    cans = "psc"
                    text = cans + " " + uans + " " + count +" " + flag
                    print("0" + text)
                elif ans == 2:
                    if user == 1:
                        flag = "1"
                    elif user == 2:
                        flag = "0"
                    else:
                        flag = "2"
                    cans = "pst"
                    text = cans + " " + uans + " " + count +" " + flag
                    print("0" + text)
                elif ans == 3:
                    if user == 1:
                        flag = "2"
                    elif user == 2:
                        flag = "1"
                    else:
                        flag = "0"
                    cans = "pp"
                    text = cans + " " + uans + " " + count +" " + flag
                    print("0" + text)

                if temp == start + 13:
                    client_executor.send(text.encode('utf-8'))
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    #except Exception as e:
    #    print(e)
    #    sys.exit(-1)



#主函式
if __name__ == '__main__':
    # IP , Port......設定
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('192.168.56.1', 8000))
    listener.listen(5)
    print('Waiting for connect...')
    #a = threading.Thread(target=camera, args=(client_executor, addr))
    #a.start()
    while True:
        client_executor, addr = listener.accept()
        t = threading.Thread(target=classfly, args=(client_executor, addr))
        t.start()