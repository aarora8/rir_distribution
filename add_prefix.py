#!/usr/bin/env python3
import sys

# P09_S03_NOLOCATION.L-0005948-0006038 P09
# P09_S03_U01_NOLOCATION.CH1-0005948-0006038 P09

# P09_S03_NOLOCATION.L-0005948-0006038 P09
# P09_S03_U01_NOLOCATION.CH1-0005948-0006038 P09
# U01CH1_P09_S03_NOLOCATION.L-0005948-0006038 P09

for line in sys.stdin:
    parts = line.strip().split()
    uttid = parts[0]

    spkrid = uttid.strip().split('_')[0]
    sessionid = uttid.strip().split('_')[1]
    arrayid = uttid.strip().split('_')[2]
    locationid = uttid.strip().split('_')[3].split('.')[0]
    channelid = uttid.strip().split('-')[0].split('.')[1]
    starttime = uttid.strip().split('-')[1]
    endtime = uttid.strip().split('-')[2]

    uttid_worn_format = arrayid + channelid + '_' + spkrid + '_' + sessionid + '_' + \
                          locationid + '.L-' + starttime + '-' + endtime

    print("{} {}".format(uttid, uttid_worn_format))