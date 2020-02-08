#!/usr/bin/env python3
# Apache 2.0.
"""Usage: make_worn_and_array_utterances_consistent.py data/train_worn data/train_u01"""
import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="""This script keeps only those utterances which
                       are present both in worn and array directory""")
    parser.add_argument("input_worn_path", type=str,
                        help="path to worn directory")
    parser.add_argument("input_array_path", type=str,
                        help="path to array directory")
    parser.add_argument("output_worn_path", type=str,
                        help="path to worn directory")
    parser.add_argument("output_array_path", type=str,
                        help="path to array directory")
    parser.add_argument("--write-worn-output", type=str,
                        choices=["true", "false"], default="false",
                        help="If worn output should be written or not")
    args = parser.parse_args()
    args.write_worn_output = bool(args.write_worn_output == "true")
    return args


def load_utt2spk(f):
    utt_dict = {}
    for line in f:
        parts = line.strip().split()
        uttid = parts[0]
        val = "_".join(parts[1:])
        utt_dict[uttid]=val
    return utt_dict


def main():
    args = get_args()
    worn_utt2spk_path = args.input_worn_path + '/' + 'text'
    array_utt2spk_path = args.input_array_path + '/' + 'text'
    wornutt_dict = load_utt2spk(open(worn_utt2spk_path, 'r', encoding='utf8'))
    arrayutt_dict = load_utt2spk(open(array_utt2spk_path, 'r', encoding='utf8'))
    array_writer = open(args.output_array_path + '/' + 'text', 'w')

    array_output_dict = {}
    worn_output_dict = {}
    for uttid in sorted(arrayutt_dict.keys()):
        worn_uttid = "_".join(uttid.strip().split('_')[1:])
        if worn_uttid not in wornutt_dict:
            continue
        array_output_dict[uttid] = arrayutt_dict[uttid]
        worn_output_dict[worn_uttid] = wornutt_dict[worn_uttid]

    if args.write_worn_output:
        worn_writer = open(args.output_worn_path + '/' + 'text', 'w')
        for uttid in sorted(worn_output_dict.keys()):
            worn_writer.write(uttid + ' ' + worn_output_dict[uttid] + '\n')

    for uttid in sorted(array_output_dict.keys()):
        array_writer.write(uttid + ' ' + array_output_dict[uttid] + '\n')

if __name__ == '__main__':
    main()