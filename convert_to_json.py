#!/usr/bin/env python3
import json
from datetime import timedelta

filename='/Users/ashisharora/Desktop/chime6/dev_beamformit_dereverb_ref_stats_seg_diarization/rttm_1_copy.txt'
recoid_dict= {}


with open(filename) as f:
    for line in f:
        parts = line.strip().split()
        sessionid_arrayid = parts[1]
        sessionid = sessionid_arrayid.split('_')[0]
        reference=sessionid_arrayid.split('_')[-1]
        start_time = float(parts[3])
        start_time_td = timedelta(seconds=start_time)

        time = str(start_time_td).split(':')
        hrs, mins, secs = time[0], time[1], float(time[2])
        secs1 = "{0:.2f}".format(secs)
        start_time_str = str(hrs) + ':'+ str(mins) + ':'+ str(secs1)

        end_time = start_time + float(parts[4])
        end_time_td=str(timedelta(seconds=end_time))

        time = str(end_time_td).split(':')
        hrs, mins, secs = time[0], time[1], float(time[2])
        secs1 = "{0:.2f}".format(secs)
        end_time_str = str(hrs) + ':' + str(mins) + ':' + str(secs1)

        spkr = parts[7]
        st = int(start_time * 100)
        end = int(end_time * 100)
        utt = "{0}-{1:06d}-{2:06d}".format(spkr, st, end)
        print(end_time_str, start_time_str, "NA", spkr, reference, "NA", sessionid)
        recoid_dict[utt] = (end_time_str, start_time_str, "NA", spkr, reference, "NA", sessionid)

count=0
output = []
with open('person.json', 'w') as json_file:
    for record_id in sorted(recoid_dict.keys()):
        person_dict = {"end_time": recoid_dict[record_id][0],
                       "start_time": recoid_dict[record_id][1],
                       "words":recoid_dict[record_id][2],
                       "speaker":recoid_dict[record_id][3],
                       "ref":recoid_dict[record_id][4],
                       "location":recoid_dict[record_id][5],
                       "session_id":recoid_dict[record_id][6]
                       }
        output.append(person_dict)
        count += 1
        if count >= 5:
            break
    json.dump(output, json_file, indent=4, separators=(',', ':'))
