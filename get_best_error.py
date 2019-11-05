#! /usr/bin/env python

"""This script finds best matching of reference and hypothesis speakers.
  For the best matching it provides the WER"""


import itertools
import numpy as np
import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description="""This script finds best matching of reference and hypothesis speakers.
  For the best matching it provides the WER""")
    parser.add_argument("WER_dir", type=str,
                        help="path of WER files")
    args = parser.parse_args()
    return args


def get_results(filename):
    with open(filename) as f:
        first_line = f.readline()
        parts = first_line.strip().split(',')
        total_words = parts[0].split()[-1]
        ins = parts[1].split()[0]
        deletions = parts[2].split()[0]
        sub = parts[3].split()[0]
        return total_words, ins, deletions, sub


def merge_results(recording_id, num_spkr, hyp_spkr_order, WER_dir):
    ref_spk_list = list()
    for i in range(1, num_spkr + 1):
        ref_spk_list.append(i)

    ins = 0
    deletion = 0
    sub = 0
    total_words = 0
    for spkr in range(num_spkr):
        filename = '/wer_' + recording_id + '_' + 'r' + str(ref_spk_list[spkr])+ 'h' + str(hyp_spkr_order[spkr]) + '_comb'
        filename = WER_dir + filename
        words, spkr_ins, spkr_del, spkr_sub = get_results(filename)
        ins += int(spkr_ins)
        deletion += int(spkr_del)
        sub += int(spkr_sub)
        total_words += int(words)
    return total_words, (ins + deletion + sub), ins, deletion, sub


def get_min_wer_perm(recording_id, num_speakers, WER_dir):
    all_errors_list = list()
    speaker_list = list()
    total_error_list = list()
    for i in range(1, num_speakers+1):
        speaker_list.append(i)

    speaker_perm = list(itertools.permutations(speaker_list))
    for spkr_order in speaker_perm:
        total_words, total_error, ins, deletion, sub = merge_results(recording_id, num_speakers, spkr_order, WER_dir)
        all_errors_list.append([total_words, total_error, ins, deletion, sub])
        total_error_list.append(total_error)

    index_min = np.argmin(total_error_list)
    print("Best spkr matching:", speaker_perm[index_min])
    print("Best error: (#T #E #I #D #S) ", all_errors_list[index_min])
    return speaker_perm[index_min], all_errors_list[index_min]


def main():
    args = get_args()
    recording_id_list = ['S02_U02.ENH' 'S09_U06.ENH', 'S02_U03.ENH', 'S09_U01.ENH', 'S09_U04.ENH']
    for recording_id in recording_id_list:
        get_min_wer_perm(recording_id, 4, args.WER_dir)


if __name__ == '__main__':
    main()