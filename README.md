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
