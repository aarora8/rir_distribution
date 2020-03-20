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

MAX_LENGTH=3600*3*16000
FS=16000


def trans_time(time, fs):
    units = time.split(':')
    time_second = float(units[0]) * 3600 + float(units[1]) * 60 + float(units[2])
    return int(time_second*fs)


def get_time(conf, tag, mic, fs):
    for i in conf:
        st = trans_time(i['start_time'][mic], fs)
        ed = trans_time(i['end_time'][mic], fs)
        tag[st:ed] = tag[st:ed] + 1
    return tag

def main():
    # args = get_args()
    out_dir='/Users/ashisharora/Desktop/chime6/output2'
    audio_list='/Users/ashisharora/Desktop/chime6/chime5_transcriptions/audio_list'
    trans_dir = '/Users/ashisharora/Desktop/chime6/chime5_transcriptions/dev'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)


    wav_list = open(audio_list).readlines()
    for i, audio in enumerate(wav_list):
        parts = audio.strip().split('.')
        session, mic = parts[0].strip().split('_')
        print(session, mic)
        tag = np.zeros(MAX_LENGTH,dtype=int)
        with open(trans_dir + "/" + session + '.json') as f:
            conf = json.load(f)
        tag = get_time(conf, tag, mic, FS)
        utt2spk_file = '/Users/ashisharora/Desktop/chime6/output2/' + mic + '_' + session
        utt2spk_fh = open(utt2spk_file, 'w')
        for j,line in enumerate(tag):
                utt2spk_fh.write(str(line) + '\n')

if __name__ == '__main__':
    main()