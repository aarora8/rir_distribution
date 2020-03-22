#!/usr/bin/env python3

import argparse
import json
import os
import scipy.io.wavfile as siw
import numpy as np
import pickle

# def get_args():
#     parser = argparse.ArgumentParser(
#         """Extract noises from the corpus based on the non-speech regions.
#         e.g. {} /export/corpora4/CHiME5/audio/train/ \\
#                 /export/corpora4/CHiME5/transcriptions/train/ \\
#                 /export/b05/zhiqiw/noise/""".format(sys.argv[0]))
#
#     parser.add_argument("--segment-length", default=20)
#     parser.add_argument("audio_dir", help="""Location of the CHiME5 Audio files. e.g. /export/corpora4/CHiME5/audio/train/""")
#     parser.add_argument("trans_dir", help="""Location of the CHiME5 Transcriptions. e.g. /export/corpora4/CHiME5/transcriptions/train/""")
#     parser.add_argument("audio_list", help="""List of ids of the CHiME5 recordings from which noise is extracted. e.g. local/distant_audio_list""")
#     parser.add_argument("out_dir", help="Output directory to write noise files. e.g. /export/b05/zhiqiw/noise/")
#
#     args = parser.parse_args()
#     return args


FS=16000
ten_millisec=int(0.01*FS)


def main():
    # args = get_args()
    segments='/Users/ashisharora/Desktop/chime6/chime6_transcriptions/segments'
    overlap_dir='/Users/ashisharora/Desktop/chime6/output2/S03'
    out_dir = '/Users/ashisharora/Desktop/chime6/output2'

    overlap_handle = open(overlap_dir, 'r')
    overlap_data = overlap_handle.read().strip().split("\n")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for line in open(segments):
        parts = line.strip().split()
        print(parts)
        if parts[1].strip().split('_')[0] != 'S03':
            continue
        st_time=int(float(parts[2])*16000)
        end_time = int(float(parts[3])*16000)
        # print(st_time, end_time)
        count=0
        for val in overlap_data[st_time+ten_millisec:end_time-ten_millisec:ten_millisec]:
            count=count+1
        print(count)


if __name__ == '__main__':
    main()