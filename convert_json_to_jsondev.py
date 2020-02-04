#!/usr/bin/env python3
# Apache 2.0.

"""This script converts an train json
        into Chime6 dev json format
Usage: convert_json_to_jsondev.py Chime6/transcription/train/S02.json
       Chime6/transcription/train/s02_new.json"""

import json
from datetime import timedelta


import argparse
def get_args():
    parser = argparse.ArgumentParser(
        description="""This script converts an train json
        into Chime6 dev json format""")
    parser.add_argument("train_json_file", type=str,
                        help="""Input json file.
                        The format of the train json file is
                        <end_time> <start_time> <words> <speaker> """
                        """<session_id>""")
    parser.add_argument("json_file", type=str,
                        help="""output json file.
                        The format of the new train json file is
                        <end_time> <start_time> <words> <speaker> """
                        """<ref> <location> <session_id>""")
    args = parser.parse_args()

    return args


def load_train_json(json_file):
    recoid_dict = {}
    with open(json_file, 'r') as jfile:
        session_dict = json.load(jfile)
        missed = 0
        for uttid in session_dict:
            try:
                end_time_hh = str(uttid['end_time'])
                start_time_hh = str(uttid['start_time'])
                words = uttid['words']
                speaker_id = uttid['speaker']
                session_id = uttid['session_id']
                utt = "{0}_{1}-{2}-{3}".format(speaker_id, session_id, start_time_hh, end_time_hh)
                recoid_dict[utt] = (end_time_hh, start_time_hh, words, speaker_id, "NA", "NA", session_id)
            except:
                missed += 1
                continue
    print(missed)
    return recoid_dict


def main():
    args = get_args()
    recoid_dict = load_train_json(args.train_json_file)
    output = []
    with open(args.json_file, 'w') as json_file:
        for record_id in sorted(recoid_dict.keys()):
            utt_dict = {"end_time": recoid_dict[record_id][0],
                           "start_time": recoid_dict[record_id][1],
                           "words": recoid_dict[record_id][2],
                           "speaker": recoid_dict[record_id][3],
                           "ref": recoid_dict[record_id][4],
                           "location": recoid_dict[record_id][5],
                           "session_id": recoid_dict[record_id][6]
                           }
            output.append(utt_dict)
        json.dump(output, json_file, indent=4, separators=(',', ':'))


if __name__ == '__main__':
    main()