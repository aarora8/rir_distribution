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
                        help="Output path for per_speaker per_recording_id reference files")
    args = parser.parse_args()
    return args


def main():
  args = get_args()

  # find all recording ids present in the text file
  # split text based on recording_id
  #P05_S02_U02_KITCHEN.ENH-0266866-0266958
  speakerid_sessionid_dict= {}
  spkrid_dict = {}
  for line in open(args.text_path):
    parts = line.strip().split()
    uttid_id = parts[0]
    spkr_id = '_'.join(uttid_id.strip().split('_')[0:1])
    speakerid_sessionid = '_'.join(uttid_id.strip().split('_')[0:2])
    if speakerid_sessionid not in list(speakerid_sessionid_dict.keys()):
      speakerid_sessionid_dict[speakerid_sessionid]=list()
    speakerid_sessionid_dict[speakerid_sessionid].append(line)
    if spkr_id not in list(spkrid_dict.keys()):
        spkrid_dict[spkr_id] = list()
    spkrid_dict[spkr_id].append(line)

  print(speakerid_sessionid_dict.keys())

  spkrid_mapping = {}
  spkr_num = 1
  for spkr_id in sorted(spkrid_dict.keys()):
    if spkr_id not in list(spkrid_mapping.keys()):
      spkrid_mapping[spkr_id] = spkr_num
      spkr_num = spkr_num + 1


  # write per recording_id text file
  for speakerid_sessionid in sorted(speakerid_sessionid_dict.keys()):
    ref_file = args.output_path + '/ref_' + speakerid_sessionid.split('_')[1] + '_' + str(spkrid_mapping[speakerid_sessionid.split('_')[0]])
    ref_writer = open(ref_file, 'w')
    text = speakerid_sessionid_dict[speakerid_sessionid]
    for line in text:
      ref_writer.write(line)
    ref_writer.close()


if __name__ == '__main__':
  main()