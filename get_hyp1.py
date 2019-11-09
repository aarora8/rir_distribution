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
    args = get_args()
    sessionid_speakerid_dict= {}
    for line in open(args.text_path):
        parts = line.strip().split()
        uttid_id = parts[0]
        speakerid = uttid_id.strip().split('-')[1]
        sessionid = uttid_id.strip().split('_')[0]
        sessionid_speakerid = sessionid + '_' + speakerid
        if sessionid_speakerid not in list(sessionid_speakerid_dict.keys()):
            sessionid_speakerid_dict[sessionid_speakerid]=list()
        sessionid_speakerid_dict[sessionid_speakerid].append(line)

    for sessionid_speakerid in sorted(sessionid_speakerid_dict.keys()):
        ref_file = args.output_path + '/' + 'hyp' + '_' + sessionid_speakerid
        ref_writer = open(ref_file, 'w')
        combined_ref_file = args.output_path + '/' + 'hyp' + '_' + sessionid_speakerid + '_comb'
        combined_ref_writer = open(combined_ref_file, 'w')
        utterances = sessionid_speakerid_dict[sessionid_speakerid]
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
