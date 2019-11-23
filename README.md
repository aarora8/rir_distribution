# rir_distribution
preserve model: steps/nnet3/chain/train.py
steps/libs/nnet3/train/common.py

cat combine.cegs | nnet3-chain-copy-egs ark:- ark,scp:combine1.cegs,combine1.scp

cat cegs.1.ark | nnet3-chain-copy-egs ark:- ark,scp:combine2.cegs,combine2.scp

cat cegs.*.ark | nnet3-chain-copy-egs ark:- ark,scp:combine3.cegs,combine3.scp

cat uttlist | cut -d'-' -f1 | sort | uniq | head

cat utt2spk | awk -v p=reverb '{printf("%s%s %s\n", p, $1, $1);}' > utt2uniq

$cmd JOB=1:20 exp/tri4_lats_nodup_aug/log/copy_out_lat.JOB.log   lattice-copy --write-compact=true "ark:gunzip -c exp/tri4_lats_nodup_aug/lat.JOB.gz |" ark,scp:exp/tri4_lats_nodup_aug/lat_tmp.JOB.ark,exp/tri4_lats_nodup_aug/lat_tmp.JOB.scp


grep Sum exp/chain/tdnn1a_aug/decode_eval2000_sw1_fsh_fg/score_10_0.0/eval2000_hires.ctm.swbd.filt.sys | utils/best_wer.sh

echo 'bar' | tee -a foo.txt

feat-to-dim scp:feats.scp -

nnet3-augment-image --srand=1 --fmask=true ark:/export/b05/aarora8/kaldi.aug/egs/swbd/s5c.bs2/exp/chain/tdnn1a_aug/egs//valid_diagnostic.cegs ark,t:-

./steps/nnet3/report/generate_plots.py --is-chain true exp/chain/tdnn1a_ep30_aug exp/chain/tdnn1a_aug exp/chain/tdnn1a_ep30_aug/report

qlogin -l 'hostname=c*,gpu=2,ram_free=4G,mem_free=4G' -now no

sclite -r chime6/data/stm_S02_U02.ENH_P05_U02 stm -h chime6/data/ctm_S02_U02.ENH_1 ctm -o all stdout | less

cat $dir/alignment_${sessionid}_r${ind_r}h${ind_h}.txt | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'"  > $wer_dir/${recording_id}_r${ind_r}h${ind_h}/wer_details/per_utt

utils/scoring/wer_per_spk_details.pl data/$dir_name/utt2spk > $wer_dir/${recording_id}_r${ind_r}h${ind_h}_ref_segmentation/wer_details/per_spk

local/wer_output_filter < data/eval_beamformit_dereverb_ref/text > text.filt.txt
if [ $stage -le 4 ]; then
ind_r=1
while IFS=: read -r recording_id spkorder
do
  IFS='_'
  read -ra hyp_spkr <<< "$spkorder"
  ind_r=1
  for ind_h in "${hyp_spkr[@]}"; do
    ind_r=$(( ind_r + 1 ))
  done
done < recordinid_spkorder
fi

recordinid_spkorder=$(<recordinid_spkorder)
recordinid_list=$(echo "$recordinid_spkorder" | cut -f1 -d ":")
spkorder_list=$(echo "$recordinid_spkorder" | cut -f2 -d ":")
while read -r line;
do
 echo " is: $recordinid";
done < <(printf '%s\n' "$recordinid_list")



S02_U01 2_4_1_3 36444 32126 88.15
S02_U02 4_1_2_3 36444 29493 80.93
S02_U03 3_1_2_4 36444 28128 77.18
S02_U04 4_1_3_2 36444 28707 78.77
S02_U06 3_4_1_2 36444 28819 79.08
S09_U01 2_1_3_4 22437 21553 96.06
S09_U02 3_4_1_2 22437 20804 92.72
S09_U03 3_1_2_4 22437 20286 90.41
S09_U04 2_1_3_4 22437 19678 87.70
S09_U06 2_3_4_1 22437 19212 85.63
U01 58881 53679 91.17
U02 58881 50297 85.42
U03 58881 48414 82.22
U04 58881 48385 82.17
U06 58881 48031 81.57
