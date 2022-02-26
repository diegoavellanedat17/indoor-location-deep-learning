import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
from datetime import datetime
from csv import writer
from csv import reader

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def save_chunk(initial_chunk,final_chunk_idx,file_chunk_name,stations,moving_average_window):
    f = open(f"{file_chunk_name}/{file_chunk_name}_{initial_chunk}.csv", "a")
    for i in range(initial_chunk, final_chunk_idx):
        f = open(f"{file_chunk_name}/{file_chunk_name}_{initial_chunk}.csv", "a")
        f.write(f"\n{str(stations[i]).replace('[ ','').replace('[','').replace('  ',' ').replace(' ',',').replace(']','')}")
        f.close()
        
    file = pd.read_csv(f"{file_chunk_name}/{file_chunk_name}_{initial_chunk}.csv",header= None)
    station1  = file.iloc[:,0].values
    station2  = file.iloc[:,1].values
    station3  = file.iloc[:,2].values
    station4  = file.iloc[:,3].values
    station5  = file.iloc[:,4].values

    
    fil_station1 = moving_average(station1,moving_average_window)
    fil_station2 = moving_average(station2,moving_average_window) 
    fil_station3 = moving_average(station3,moving_average_window) 
    fil_station4 = moving_average(station4,moving_average_window) 
    fil_station5 = moving_average(station5,moving_average_window)

    table = np.asarray([fil_station1,fil_station2,fil_station3,fil_station4,fil_station5])
    np.savetxt(f"{file_chunk_name}_fil/{file_chunk_name}_{initial_chunk}.csv",table.transpose(),delimiter=",")

    with open(f"{file_chunk_name}_fil/{file_chunk_name}_{initial_chunk}.csv", 'r') as read_obj, \
        open(f"{file_chunk_name}_fil_t/{file_chunk_name}_{initial_chunk}.csv", 'w', newline='') as write_obj:

        csv_reader = reader(read_obj)
        csv_writer = writer(write_obj)
        csv_writer.writerow(("Station1", "Station2", "Station3", "Station4","Station5","timestamp"))
        for idx, row in enumerate(csv_reader):
            row.append(idx)
            csv_writer.writerow(row)
    
    # Cov= pd.read_csv(f"{file_chunk_name}_fil_t/{file_chunk_name}_{initial_chunk}.csv", 
    #               sep='\t', 
    #               names=["Station1", "Station2", "Station3", "Station4","Station5","timestamp"])
    # print(Cov)

# Numero de muestras por ventana de tiempo 
n_receive_chunk = 10
window_moves = 1
moving_average_window = 3
initial_chunk = 0
final_chunk_idx = n_receive_chunk
train_coordinates_filename  = '2,2'

file = pd.read_csv('./dataCoordinates/2,2.csv',header= None)
stations  = file.iloc[:,0:5].values
  

while final_chunk_idx < len(stations):
    os.makedirs(os.path.dirname(f'{train_coordinates_filename}/'), exist_ok=True)
    os.makedirs(os.path.dirname(f'{train_coordinates_filename}_fil/'), exist_ok=True)
    os.makedirs(os.path.dirname(f'{train_coordinates_filename}_fil_t/'), exist_ok=True)
    save_chunk(initial_chunk,final_chunk_idx,train_coordinates_filename,stations,moving_average_window)
    initial_chunk = initial_chunk + window_moves
    final_chunk_idx= final_chunk_idx + window_moves
    
#fil_station1= moving_average(station1,3)

# fig,ax = plt.subplots()
# ax.plot(fil_station1); 
# plt.show()

