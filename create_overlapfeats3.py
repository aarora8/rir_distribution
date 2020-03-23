#!/usr/bin/env python3

import argparse
import json
import os
import numpy as np
import sys
from glob import glob
def get_args():
    parser = argparse.ArgumentParser(
        """Extract noises from the corpus based on the non-speech regions.
        e.g. {} /export/corpora4/CHiME5/transcriptions/train/ \\
                local/worn_audio_list data/distant_overlap""".format(sys.argv[0]))

    parser.add_argument("data_dir", help="""Location of the CHiME5 Transcriptions. e.g. /export/corpora4/CHiME5/transcriptions/train/""")
    parser.add_argument("overlap_dir", help="Output directory to write noise files. e.g. data/distant_overlap")

    args = parser.parse_args()
    return args

FS=16000
ten_millisec=int(0.01*FS)


def main():
    args = get_args()
    segment_handle = open(os.path.join(args.data_dir,'segments'), 'r')
    segment_data = segment_handle.read().strip().split("\n")
    output_fh = open(os.path.join(args.data_dir,'worn_overlap3'), 'w')
    all_files = os.listdir(args.overlap_dir)
    for file in all_files:
        overlap_handle = open(os.path.join(args.overlap_dir,file), 'r')
        overlap_data = overlap_handle.read().strip().split("\n")
        for line in segment_data:
            parts = line.strip().split()
            if parts[1].strip().split('.')[0] != file:
                continue
            st_time=int(float(parts[2])*16000)
            end_time = int(float(parts[3])*16000)
            #count=0
            #for val in overlap_data[st_time+ten_millisec:end_time-ten_millisec:ten_millisec]:
            #    count=count+1
            #print(count)
            #output_fh.write(parts[0].strip() + ' [')
            #for val in overlap_data[st_time+ten_millisec:end_time-2*ten_millisec:ten_millisec]:
            #    output_fh.write(str(val) + '\n')
            #final_val = str(overlap_data[end_time-ten_millisec])
            #output_fh.write(output_fh.write('ashish' + '\n'))
            output_fh.write(parts[0].strip() + ' [')
            for val in overlap_data[st_time+ten_millisec:end_time-2*ten_millisec:ten_millisec]:
                output_fh.write(str(val) + '\n')
            val = overlap_data[end_time-ten_millisec]
            output_fh.write(str(val) + ' ]' + '\n')
            output_fh.write('\n')


if __name__ == '__main__':
    main()
