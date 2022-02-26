# In this file is the main code for locate TAGS in the space. 
import collections
import numpy as np
import random

window_size = 10 
rssi_queue = collections.deque(window_size*[0], maxlen=window_size)
rssi_data = list(rssi_queue)
moving_average_window = 3

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


for item in range(15):
    # simulate incomming data for each 
    rand = random.randint(30, 90)*-1
    item_data = [[-100,-100,-100,-100,-100],[-3,rand+1,rand+2,rand+3,rand+4],[-100,-100,-100,-100,-100]]
    process_info(item_data)
#rssi_array = np.array(rssi_queue)
