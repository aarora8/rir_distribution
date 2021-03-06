#! /usr/bin/env python

"""This script splits a kaldi (text) file
  into per_speaker per_recording_id reference (text) file"""

import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description="""This script splits a kaldi text file
        into perspeaker per_recording_id  text files""")
    parser.add_argument("text_path", type=str,
                        help="path of text files")
    parser.add_argument("output_path", type=str,
                        help="Output path for per_session per_speaker reference files")
    args = parser.parse_args()
    return args


def main():
    # P05_S02_U02_KITCHEN.ENH-0266866-0266958
    # S09_U06.ENH-4-704588-704738
    args = get_args()
    sessionid__micid_speakerid_dict= {}
    for line in open(args.text_path):
        parts = line.strip().split()
        uttid_id = parts[0]
        temp = uttid_id.strip().split('.')[0]
        micid = temp.strip().split('_')[1]
        speakerid = uttid_id.strip().split('-')[1]
        sessionid = uttid_id.strip().split('_')[0]
        sessionid__micid_speakerid = sessionid + '_' + micid + '_' + speakerid
        if sessionid__micid_speakerid not in list(sessionid__micid_speakerid_dict.keys()):
            sessionid__micid_speakerid_dict[sessionid__micid_speakerid]=list()
        sessionid__micid_speakerid_dict[sessionid__micid_speakerid].append(line)

    for sessionid__micid_speakerid in sorted(sessionid__micid_speakerid_dict.keys()):
        ref_file = args.output_path + '/' + 'hyp' + '_' + sessionid__micid_speakerid
        ref_writer = open(ref_file, 'w')
        combined_ref_file = args.output_path + '/' + 'hyp' + '_' + sessionid__micid_speakerid + '_comb'
        combined_ref_writer = open(combined_ref_file, 'w')
        utterances = sessionid__micid_speakerid_dict[sessionid__micid_speakerid]
        text = ''
        for line in utterances:
            parts = line.strip().split()
            text = text + ' ' + ' '.join(parts[1:])
            ref_writer.write(line)
        combined_utterance = 'utt' + " " + text
        combined_ref_writer.write(combined_utterance)
        combined_ref_writer.close()
        ref_writer.close()


if __name__ == '__main__':
    main()

