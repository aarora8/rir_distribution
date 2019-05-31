import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math

Room_x = list()
Room_y = list()
Room_z = list()

Mic_x = list()
Mic_y = list()
Mic_z = list()

Source_x = list()
Source_y = list()
Source_z = list()

rt60_list = list()
azimuth_degree_list = list()
elevation_degree_list = list()
radii_list = list()


text_file = os.path.join('/Users/ashisharora/Desktop/dct/plots' + '/', 'text1')
text_fh = open(text_file, 'r')
line_vect = text_fh.read().strip().split("\n")
for line in line_vect:
    rir_parameter = line.split(' ')
    room_x = float(rir_parameter[0][1:-1])
    room_y = float(rir_parameter[1][1:-1])
    room_z = float(rir_parameter[2][1:-1])
    mic_x = float(rir_parameter[3][1:-1])
    mic_y = float(rir_parameter[4][1:-1])
    mic_z = float(rir_parameter[5][1:-1])
    source_x = float(rir_parameter[6][1:-1])
    source_y = float(rir_parameter[7][1:-1])
    source_z = float(rir_parameter[8][1:-1])
    rt60 = float(rir_parameter[9])
    azimuth_degree = float(rir_parameter[10][1:-1])
    elevation_degree = float(rir_parameter[11][1:-1])
    radii = float(rir_parameter[12])

    Room_x.append(room_x)
    Room_y.append(room_y)
    Room_z.append(room_z)

    Mic_x.append(mic_x)
    Mic_y.append(mic_y)
    Mic_z.append(mic_z)

    Source_x.append(source_x)
    Source_y.append(source_y)
    Source_z.append(source_z)

    rt60_list.append(rt60)
    azimuth_degree_list.append(azimuth_degree)
    elevation_degree_list.append(elevation_degree)
    radii_list.append(radii)


print(Room_x[1:20])
plt.hist(rt60_list, bins='auto',alpha=0.7)
# plt.hist(Room_y, bins='auto',alpha=0.7)
# plt.hist(Room_z, bins='auto',alpha=0.7)
#
# plt.hist(rt60_list, bins='auto',alpha=0.7)
# plt.hist(radii_list, bins='auto',alpha=0.7)
# plt.hist(azimuth_degree_list, bins='auto',alpha=0.7)
# plt.hist(elevation_degree_list, bins='auto',alpha=0.7)

plt.show()