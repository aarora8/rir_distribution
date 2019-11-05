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
  #'P05_S02_U02_KITCHEN.ENH-0004062-0004384 it's the blue i think i think'
  recoid_dict= {}
  for line in open(args.text_path):
    parts = line.strip().split()
    uttid_id = parts[0]
    reco_id = '_'.join(uttid_id.strip().split('_')[1:3])
    reco_id = reco_id + '.ENH'
    if reco_id not in list(recoid_dict.keys()):
      recoid_dict[reco_id]=list()
    recoid_dict[reco_id].append(line)

  print(recoid_dict.keys())

  # write per recording_id text file
  for record_id in sorted(recoid_dict.keys()):
    ref_file = args.output_path + '/ref_' + str(record_id)
    ref_writer = open(ref_file, 'w')
    text = recoid_dict[record_id]
    for line in text:
      ref_writer.write(line)
    ref_writer.close()


  # find all spkr id present in the per recording_id text file
  # split text based on speaker_id
  for record_id in sorted(recoid_dict.keys()):
    spkrid_dict = {}
    ref_file = args.output_path + '/ref_' + str(record_id)
    for line in open(ref_file):
      parts = line.strip().split()
      uttid_id = parts[0]
      reco_id = '_'.join(uttid_id.strip().split('_')[1:3])
      spkr_id = uttid_id.strip().split('_')[0]
      if spkr_id not in list(spkrid_dict.keys()):
        spkrid_dict[spkr_id] = list()
      spkrid_dict[spkr_id].append(line)

    print(spkrid_dict.keys())

    spkrid_mapping = {}
    spkr_num = 1
    for spkr_id in sorted(spkrid_dict.keys()):
        if spkr_id not in list(spkrid_mapping.keys()):
            spkrid_mapping[spkr_id] = spkr_num
            spkr_num = spkr_num + 1

    # split text based on speaker_id
    for spkr_id in sorted(spkrid_dict.keys()):
      ref_file = args.output_path + '/ref_' + str(record_id) + '_' + str(spkrid_mapping[spkr_id])
      combined_ref = args.output_path + '/ref_' + str(record_id) + '_' + str(spkrid_mapping[spkr_id]) + '_comb'
      ref_writer = open(ref_file, 'w')
      combined_ref_writer = open(combined_ref, 'w')
      text = ''
      utterances = spkrid_dict[spkr_id]
      for line in utterances:
        parts = line.strip().split()
        ref_writer.write(line)
        if (len(parts) == 1):
            continue
        text = text + ' ' + ' '.join(parts[1:])
      combined_utterance = 'utt' + " " + text
      ref_writer.close()
      combined_ref_writer.write(combined_utterance)
      combined_ref_writer.close()


if __name__ == '__main__':
  main()