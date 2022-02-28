# In this file is the main code for locate TAGS in the space. 
import collections
import numpy as np
import random
import paho.mqtt.client as mqtt
import re
import json
from datetime import datetime, timedelta
from mqtt_connection import *
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.runner import ImpulseRunner
import io

window_size = 10 
rssi_queue = collections.deque(window_size*[0], maxlen=window_size)
rssi_data = list(rssi_queue)
moving_average_window = 3
runner = None
model = '4classesModel.eim'
dir_path = os.path.dirname(os.path.realpath(__file__))
modelfile = os.path.join(dir_path, model)

def signal_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def help():
    print('python classify.py <path_to_model.eim> <path_to_features.txt>')

def on_connect(client, userdata, flags, rc):
    # This will be called once the client connects
    print(f"Connected with result code {rc}")
    # Subscribe here!
    client.subscribe("station1")
    client.subscribe("station2")
    client.subscribe("station3")
    client.subscribe("station4")
    client.subscribe("station5")

def time_map(now):
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string

def on_message(client, userdata, msg):
    global rssi_vector
    payload = msg.payload.decode("utf-8")
    #print(f'Topic {msg.topic} ---> Payload {msg.payload}')
    #payload = payload.replace("\\", "")
    try:
        payload = json.loads(payload)
        topic = msg.topic
        now = datetime.now()
        station_number = re.findall(r'[0-9]|$', topic)[0]
        tags_tupple = get_tags(payload)
        for tag_info in tags_tupple:
            if rssi_vector[tag_info[0]-1][int(station_number)-1] != 0:
                print('dato repetido')
            else:
                rssi_vector[tag_info[0]-1][int(station_number)-1] = tag_info[1]
                complete_count = 0
                for i in range(0, 3):
                    if not is_zero(rssi_vector[i]):
                        complete_count = complete_count + 1
                if complete_count == 3:
                    print('complete vector')
                    print(rssi_vector, time_map(datetime.now()))
                    process_info(rssi_vector)
                    # for i in range(0, 3):
                    #     save_data(f'TAG{i+1}.txt', f'{rssi_vector[i]},{time_map(datetime.now())}')
                    rssi_vector = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    except:
        print('algo raro')

def is_zero(vector):
    zero = False
    for item in vector:
        if item == 0:
            return True
    return zero

def get_tags(payload):
    tags_list = []
    devices = payload['devices']
    for tag in devices:
        tag_number = re.findall(r'[0-9]|$', tag['name'])[0]
        tags_list.append([int(tag_number), tag['rssi']])

    for i in range(1, 4):
        exist_flag = False
        for tag_iterator in tags_list:
          if i == tag_iterator[0]:
              exist_flag = True

        if not exist_flag:
            tags_list.append([i, -100])

    return tags_list

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def process_info(item_payload_array):
    rssi_queue.append(item_payload_array)
    tag1_rssi=[]
    tag2_rssi=[]
    tag3_rssi=[]
    if not 0 in rssi_queue:
        print('---------------------iterator------------')
        for tag_rssi in rssi_queue:
            tag1_rssi.append(tag_rssi[0])
            tag2_rssi.append(tag_rssi[1])
            tag3_rssi.append(tag_rssi[2])

        tag1_matrix = np.matrix(tag1_rssi).transpose()
        tag2_matrix = np.matrix(tag2_rssi).transpose()
        tag3_matrix = np.matrix(tag3_rssi).transpose()

        tag2_station1 = np.array(tag2_matrix[0])[0]
        tag2_station2 = np.array(tag2_matrix[1])[0]
        tag2_station3 = np.array(tag2_matrix[2])[0]
        tag2_station4 = np.array(tag2_matrix[3])[0]
        tag2_station5 = np.array(tag2_matrix[4])[0]

        s1_t2_fil = moving_average(tag2_station1,moving_average_window)
        s2_t2_fil = moving_average(tag2_station2,moving_average_window)
        s3_t2_fil = moving_average(tag2_station3,moving_average_window)
        s4_t2_fil = moving_average(tag2_station4,moving_average_window)
        s5_t2_fil = moving_average(tag2_station5,moving_average_window)

        tag2_fil = np.column_stack((s1_t2_fil,s2_t2_fil,s3_t2_fil,s4_t2_fil,s5_t2_fil))
        tag2_fil = tag2_fil.flatten()
        res = runner.classify(tag2_fil)
        print(tag2_fil)
        print("classification:")
        print(res["result"])


# for item in range(15):
#     # simulate incomming data for each 
#     rand = random.randint(30, 90)*-1
#     item_data = [[-100,-100,-100,-100,-100],[-3,rand+1,rand+2,rand+3,rand+4],[-100,-100,-100,-100,-100]]
#     process_info(item_data)
#rssi_array = np.array(rssi_queue)
print('MODEL: ' + modelfile)
runner = ImpulseRunner(modelfile)
model_info = runner.init()
print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
rssi_vector = [ [0, 0, 0, 0,0], [0, 0, 0, 0, 0], [ 0, 0, 0, 0,0]]
client = mqtt.Client("mqtt-location-script") # client ID "mqtt-test"
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_username, mqtt_password)
client.connect(mqtt_host, mqtt_port)
client.loop_forever()  # Start networking daemon
