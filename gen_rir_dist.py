import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math

sampling_rate = 16000
dist_t60=[0.04, 0.06, 0.08, 0.1, .13, 0.17, .17, 0.13, 0.08, 0.04]
t60 = np.random.choice(len(dist_t60), 100000, p=dist_t60)
plt.hist(t60/10, bins='auto',alpha=0.7)

dist_tmd=[.1425, .215, .285, .21, .09, .05, .0075]
tar_mic_dis = np.random.choice(len(dist_tmd), 100000, p=dist_tmd)
tar_mic_dis += 1
plt.hist(tar_mic_dis, bins='auto',alpha=0.7)

width = np.random.uniform(3,10,100000)
plt.hist(width, bins='auto',alpha=0.7)

length = np.random.uniform(3,8,100000)
plt.hist(length, bins='auto',alpha=0.7)

height = np.random.uniform(2.5,6,100000)
plt.hist(height, bins='auto',alpha=0.7)

total_count = 0
for i in range(0, 1000):
    rt60 = t60[i]
    room_x = width[i]
    room_y = length[i]
    room_z = height[i]

    # at least 1 meters away from the wall
    mic_x = np.random.uniform(1, (room_x - 1), 1)
    mic_y = np.random.uniform(1, (room_y - 1), 1)
    mic_z = np.random.uniform(1, (room_z - 1), 1)
    count = 0
    for rir_id in range(0, 100):
        print(rir_id)
        while True:
            count += 1
            total_count += 1
            azimuth_degree = np.random.uniform(-180, 180, 1)
            elevation_degree = np.random.uniform(45, 135, 1)
            azimuth_rad = math.radians(azimuth_degree)
            elevation_rad = math.radians(elevation_degree)
            radii = tar_mic_dis[i]
            offset_x = radii * math.cos(elevation_rad) * math.cos(azimuth_rad)
            offset_y = radii * math.cos(elevation_rad) * math.sin(azimuth_rad)
            offset_z = radii * math.sin(elevation_rad)

            source_x = offset_x + mic_x
            source_y = offset_y + mic_y
            source_z = offset_z + mic_z

            if count > 100:
                if radii > 1:
                    radii -= 1
                else:
                    radii /= 2

                mic_x = np.random.uniform(1, (room_x - 1), 1)
                mic_y = np.random.uniform(1, (room_y - 1), 1)
                mic_z = np.random.uniform(1, (room_z - 1), 1)
                print("error")
                print(total_count)
                count = 0

            if count > 100:
                mic_x = np.random.uniform(1, (room_x - 1), 1)
                mic_y = np.random.uniform(1, (room_y - 1), 1)
                mic_z = np.random.uniform(1, (room_z - 1), 1)
                print("error")
                count = 0

            #at least 0.5 meters away from the wall
            if source_x < (room_x - 0.5) and source_y < (room_y - 0.5) and source_z < (room_z - 0.5) \
                    and source_x > 0.5 and source_y > 0.5 and source_z > 0.5:
                break








# plt.title('t60')
# plt.show()

# room_dim = [4.2, 3.4, 5.2] # in meters
# rt60 = 0.4 # in seconds
# absorption = roomsimove_single.rt60_to_absorption(room_dim, rt60)
# room = roomsimove_single.Room(room_dim, abs_coeff=absorption)
#
# mic_pos = [2, 2, 2] # in  meters
# mic = roomsimove_single.Microphone(mic_pos, 1,
#         orientation=[0.0, 0.0, 0.0], direction='omnidirectional')
# mics = [mic]
# sampling_rate = 16000
# sim_rir = roomsimove_single.RoomSim(sampling_rate, room, mics, RT60=rt60)
# source_pos = [1, 1, 1] # in  meters
# rir =sim_rir.create_rir(source_pos)

# x = r .* cos(elevation) .* cos(azimuth)
# y = r .* cos(elevation) .* sin(azimuth)
# z = r .* sin(elevation)

# p=[0.07, 0.1, 0.14, 0.17, .17, 0.14, .1, 0.05, 0.03, 0.02, 0.01]
# snr = np.random.choice(len(p), 100000, p=p)
# plt.hist(snr*3, bins='auto',alpha=0.7)

# if count > 100:
#     if radii > 1:
#         radii -= 1
#     else:
#         radii /= 2
#     count = 0