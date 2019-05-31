import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import os

sampling_rate = 16000
dist_t60 = [0.04, 0.06, 0.08, 0.1, .13, 0.17, .17, 0.13, 0.08, 0.04]
t60 = np.random.choice(len(dist_t60), 200000, p=dist_t60)
t60 = t60/10
plt.hist(t60, bins='auto',alpha=0.7)

dist_tmd = [.1425, .215, .285, .21, .09, .05, .0075]
tar_mic_dis = np.random.choice(len(dist_tmd), 200000, p=dist_tmd)
tar_mic_dis += 1
plt.hist(tar_mic_dis, bins='auto',alpha=0.7)

width = np.random.uniform(3, 10, 100000)
plt.hist(width, bins='auto',alpha=0.7)

length = np.random.uniform(3, 8, 100000)
plt.hist(length, bins='auto', alpha=0.7)

height = np.random.uniform(2.5, 6, 100000)
plt.hist(height, bins='auto', alpha=0.7)

text_file = os.path.join('/Users/ashisharora/Desktop/dct/plots' + '/', 'text2')
text_fh = open(text_file, 'w')

total_count = 0
count = 0
room_x = 0
room_y = 0
room_z = 0
mic_x = 0
mic_y = 0
mic_z = 0
source_x = 0
source_y = 0
source_z = 0

for i in range(0, 200000):
    rt60 = t60[i]
    radii = tar_mic_dis[i]
    while True:
        total_count += 1
        room_x = np.random.uniform(3, 10, 1)
        room_y = np.random.uniform(3, 8, 1)
        room_z = np.random.uniform(2.5, 6, 1)

        # at least 1 meters away from the wall
        mic_x = np.random.uniform(1, (room_x - 1), 1)
        mic_y = np.random.uniform(1, (room_y - 1), 1)
        mic_z = np.random.uniform(1, (room_z - 1), 1)

        azimuth_degree = np.random.uniform(-180, 180, 1)
        elevation_degree = np.random.uniform(45, 135, 1)
        azimuth_rad = math.radians(azimuth_degree)
        elevation_rad = math.radians(elevation_degree)

        offset_x = radii * math.cos(elevation_rad) * math.cos(azimuth_rad)
        offset_y = radii * math.cos(elevation_rad) * math.sin(azimuth_rad)
        offset_z = radii * math.sin(elevation_rad)

        source_x = offset_x + mic_x
        source_y = offset_y + mic_y
        source_z = offset_z + mic_z

        #at least 0.5 meters away from the wall
        if source_x < (room_x - 0.5) and source_y < (room_y - 0.5) and source_z < (room_z - 0.5)\
                and source_x > 0.5 and source_y > 0.5 and source_z > 0.5:

            total_count = 0
            text_fh.write(
                str(room_x) + ' ' + str(room_y) + ' ' + str(room_z) + ' ' + str(mic_x) + ' ' + str(mic_y) + ' ' + str(
                    mic_z) + ' ' + str(source_x) + ' ' + str(source_y) + ' ' + str(source_z) + ' ' + str(rt60) + ' ' +
                    str(azimuth_degree) + ' ' + str(elevation_degree) + ' ' + str(radii) + '\n')
            break

        if total_count > 1000:
            count += 1
            total_count = 0
            print("count break")
            break


print("total breaks")
print(count)

