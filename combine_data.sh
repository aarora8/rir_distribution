#!/bin/bash
echo "$0 $@"  # Print the command line for logging

#. ./cmd.sh
#. ./path.sh
#. utils/parse_options.sh || exit 1;

if [ $# != 2 ]; then
  echo "Usage: combine_data.sh <dest-data-dir> <src-data-dir1>"
  exit 1
fi

in_dir=$1;
out_dir=$2;

rm -r $out_dir 2>/dev/null
mkdir -p $out_dir;

if [ ! -f $in_dir/utt2spk ]; then
  echo "$0: no such file $in_dir/utt2spk"
  exit 1;
fi

for file in utt2spk utt2lang utt2dur utt2num_frames feats.scp text cmvn.scp vad.scp reco2file_and_channel spk2gender; do

  if [ -f $in_dir/$file ]; then
    cat $in_dir/$file | ./add_prefix.py > $out_dir/$file
    echo "$0: combined $file"
  fi
done

utils/utt2spk_to_spk2utt.pl <$out_dir/utt2spk >$out_dir/spk2utt