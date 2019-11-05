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

  # find all recording ids present in the hyp file
  # split text based on recording_id
  recoid_dict= {}
  recording_path = args.output_path + '/recording_id'
  recordingid_writer = open(recording_path, 'w')
  for line in open(args.text_path):
    parts = line.strip().split()
    uttid_id = parts[0]
    reco_id = uttid_id.strip().split('-')[0]
    if reco_id not in list(recoid_dict.keys()):
      recoid_dict[reco_id]=list()
      recordingid_writer.write(reco_id + '\n')
    recoid_dict[reco_id].append(line)

  print(recoid_dict.keys())

  # write per recording_id text file
  for record_id in sorted(recoid_dict.keys()):
    hyp_file = args.output_path + '/hyp_' + str(record_id)
    hyp_writer = open(hyp_file, 'w')
    text = recoid_dict[record_id]
    for line in text:
      hyp_writer.write(line)
    hyp_writer.close()


  # find all spkr id present in the per recording_id text file
  # split text based on speaker_id
  for record_id in sorted(recoid_dict.keys()):
    spkrid_dict = {}
    hyp_file = args.output_path + '/hyp_' + str(record_id)
    for line in open(hyp_file):
      parts = line.strip().split()
      uttid_id = parts[0]
      reco_id = uttid_id.strip().split('-')[0]
      spkr_id = uttid_id.strip().split('-')[1]
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
      hyp_file = args.output_path + '/hyp_' + str(record_id) + '_' + str(spkrid_mapping[spkr_id])
      combined_hyp = args.output_path + '/hyp_' + str(record_id) + '_' + str(spkrid_mapping[spkr_id]) + '_comb'
      hyp_writer = open(hyp_file, 'w')
      combined_hyp_writer = open(combined_hyp, 'w')
      text = ''
      utterances = spkrid_dict[spkr_id]
      for line in utterances:
        parts = line.strip().split()
        hyp_writer.write(line)
        if len(parts) == 1:
            continue
        text = text + ' ' + ' '.join(parts[1:])
      combined_utterance = 'utt' + " " + text
      hyp_writer.close()
      combined_hyp_writer.write(combined_utterance)
      combined_hyp_writer.close()


if __name__ == '__main__':
  main()