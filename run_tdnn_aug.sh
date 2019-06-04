#!/bin/bash

# This recipe does multi-style training of TDNN model

# local/chain/compare_wer_general.sh --rt03 tdnn7q_sp tdnn1a_aug
# System                tdnn7q_sp tdnn1a_aug
# WER on train_dev(tg)      11.91     12.06
# WER on train_dev(fg)      10.99     10.92
# WER on eval2000(tg)        14.3      14.4
# WER on eval2000(fg)        12.8      12.9
# WER on rt03(tg)            17.2      17.1
# WER on rt03(fg)            15.1      14.8
# Final train prob         -0.062    -0.087
# Final valid prob         -0.074    -0.105
# Final train prob (xent)        -0.933    -1.164
# Final valid prob (xent)       -0.9027   -1.2246
# Num-parameters               18693376  18483664

set -e -o pipefail

stage=0
train_stage=-10
get_egs_stage=-10
num_epochs=10

# Augmentation options
aug_list="reverb clean" # Original train dir is referred to as `clean`
num_reverb_copies=1
use_ivectors=false

affix=1g1
suffix="_aug"

# training options
frames_per_eg=140,100,160
remove_egs=false
common_egs_dir=
xent_regularize=0.1
dropout_schedule='0,0@0.20,0.5@0.50,0'

# End configuration section.
echo "$0 $@"  # Print the command line for logging

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

if ! cuda-compiled; then
  cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.
EOF
fi

gmm=tri4b
clean_set=train_si284
train_set=$clean_set$suffix
clean_ali=${gmm}_ali_$clean_set
train_ali=$clean_ali$suffix
clean_lat=${gmm}_lats_$clean_set
train_lat=${gmm}_lats_$train_set
train_data_dir=data/${train_set}_hires
dir=exp/chain/tdnn$affix$suffix
tree_dir=exp/chain/tree_a
lang=data/lang_chain

nj=30
test_sets="test_dev93 test_eval92"
nnet3_affix=       # affix for exp dirs, e.g. it was _cleaned in tedlium.
reporting_email=
srand=0

#if [ $stage -le 0 ]; then
#  steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" \
#    data/$clean_set data/lang exp/$gmm exp/$clean_ali
#fi
#
## First creates augmented data and then extracts features for it data
## The script also creates alignments for aug data by copying clean alignments
#local/nnet3/multi_condition/run_aug_common.sh --stage $stage \
#  --aug-list "$aug_list" --num-reverb-copies $num_reverb_copies \
#  --use-ivectors "$use_ivectors" \
#  --train-set $clean_set --clean-ali $clean_ali || exit 1;

if [ $stage -le 11 ]; then
  # Get the alignments as lattices (gives the LF-MMI training more freedom).
  # use the same num-jobs as the alignments
  prefixes=""
  include_original=false
  for n in $aug_list; do
    if [ "$n" == "reverb" ]; then
      for i in `seq 1 $num_reverb_copies`; do
        prefixes="$prefixes "reverb$i
      done
    elif [ "$n" != "clean" ]; then
      prefixes="$prefixes "$n
    else
      # The original train directory will not have any prefix
      # include_original flag will take care of copying the original lattices
      include_original=true
    fi
  done
  nj=$(cat exp/$clean_ali$suffix/num_jobs) || exit 1;
  steps/align_fmllr_lats.sh --nj $nj --cmd "$train_cmd" data/$clean_set \
    data/lang exp/$gmm exp/$clean_lat
  rm exp/$clean_lat/fsts.*.gz # save space
  steps/copy_lat_dir.sh --nj $nj --cmd "$train_cmd" \
    --include-original "$include_original" --prefixes "$prefixes" \
    data/$train_set exp/$clean_lat exp/$train_lat || exit 1;

  if [[ $aug_list =~ "clean" ]]; then
    echo "$0: clean data already present, continuing"
  else
    include_original=true
    steps/copy_lat_dir.sh --nj $nj --cmd "$train_cmd" \
      --include-original "$include_original" --prefixes "$prefixes" \
      data/${train_set}_clean exp/$clean_lat exp/${train_lat}_clean || exit 1;
  fi
fi

if [ $stage -le 12 ]; then
  # Create a version of the lang/ directory that has one state per phone in the
  # topo file. [note, it really has two states.. the first one is only repeated
  # once, the second one has zero or more repeats.]
  rm -rf $lang
  cp -r data/lang $lang
  silphonelist=$(cat $lang/phones/silence.csl) || exit 1;
  nonsilphonelist=$(cat $lang/phones/nonsilence.csl) || exit 1;
  # Use our special topology... note that later on may have to tune this
  # topology.
  steps/nnet3/chain/gen_topo.py $nonsilphonelist $silphonelist >$lang/topo
fi

if [ $stage -le 13 ]; then
  # Build a tree using our new topology. This is the critically different
  # step compared with other recipes.
  if [ -f $tree_dir/final.mdl ]; then
     echo "$0: $tree_dir/final.mdl already exists, refusing to overwrite it."
     exit 1;
  fi
  steps/nnet3/chain/build_tree.sh --frame-subsampling-factor 3 \
      --context-opts "--context-width=2 --central-position=1" \
      --cmd "$train_cmd" 3500 data/$train_set $lang exp/$train_ali $tree_dir
fi


if [ $stage -le 14 ]; then
  mkdir -p $dir
  echo "$0: creating neural net configs using the xconfig parser";
  num_targets=$(tree-info $tree_dir/tree |grep num-pdfs|awk '{print $2}')
  learning_rate_factor=$(echo "print(0.5/$xent_regularize)" | python)
  tdnn_opts="l2-regularize=0.01 dropout-proportion=0.0 dropout-per-dim-continuous=true"
  tdnnf_opts="l2-regularize=0.01 dropout-proportion=0.0 bypass-scale=0.66"
  linear_opts="l2-regularize=0.01 orthonormal-constraint=-1.0"
  prefinal_opts="l2-regularize=0.01"
  output_opts="l2-regularize=0.005"

  mkdir -p $dir/configs
  cat <<EOF > $dir/configs/network.xconfig
  input dim=40 name=input
  # please note that it is important to have input layer with the name=input
  # as the layer immediately preceding the fixed-affine-layer to enable
  # the use of short notation for the descriptor
  fixed-affine-layer name=lda input=Append(-1,0,1) affine-transform-file=$dir/configs/lda.mat

  # the first splicing is moved before the lda layer, so no splicing here
  relu-batchnorm-dropout-layer name=tdnn1 $tdnn_opts dim=1024
  tdnnf-layer name=tdnnf2 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=1
  tdnnf-layer name=tdnnf3 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=1
  tdnnf-layer name=tdnnf4 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=1
  tdnnf-layer name=tdnnf5 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=0
  tdnnf-layer name=tdnnf6 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf7 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf8 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf9 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf10 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf11 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf12 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  tdnnf-layer name=tdnnf13 $tdnnf_opts dim=1024 bottleneck-dim=128 time-stride=3
  linear-component name=prefinal-l dim=192 $linear_opts

  prefinal-layer name=prefinal-chain input=prefinal-l $prefinal_opts big-dim=1024 small-dim=192
  output-layer name=output include-log-softmax=false dim=$num_targets $output_opts

  prefinal-layer name=prefinal-xent input=prefinal-l $prefinal_opts big-dim=1024 small-dim=192
  output-layer name=output-xent dim=$num_targets learning-rate-factor=$learning_rate_factor $output_opts
EOF
  steps/nnet3/xconfig_to_configs.py --xconfig-file $dir/configs/network.xconfig --config-dir $dir/configs/
fi

if [ $stage -le 15 ]; then
  if [[ $(hostname -f) == *.clsp.jhu.edu ]] && [ ! -d $dir/egs/storage ]; then
    utils/create_split_dir.pl \
     /export/b0{3,4,5,6}/$USER/kaldi-data/egs/wsj-$(date +'%m_%d_%H_%M')/s5/$dir/egs/storage $dir/egs/storage
  fi

  steps/nnet3/chain/train.py --stage=$train_stage \
    --cmd="$train_cmd" \
    --feat.cmvn-opts="--norm-means=false --norm-vars=false" \
    --chain.xent-regularize $xent_regularize \
    --chain.leaky-hmm-coefficient=0.1 \
    --chain.l2-regularize=0.0 \
    --chain.apply-deriv-weights=false \
    --chain.lm-opts="--num-extra-lm-states=2000" \
    --trainer.dropout-schedule $dropout_schedule \
    --trainer.add-option="--optimization.memory-compression-level=2" \
    --trainer.srand=$srand \
    --trainer.max-param-change=2.0 \
    --trainer.num-epochs=15 \
    --trainer.frames-per-iter=5000000 \
    --trainer.optimization.num-jobs-initial=2 \
    --trainer.optimization.num-jobs-final=8 \
    --trainer.optimization.initial-effective-lrate=0.0005 \
    --trainer.optimization.final-effective-lrate=0.00005 \
    --trainer.num-chunk-per-minibatch=128,64 \
    --trainer.optimization.momentum=0.0 \
    --egs.chunk-width=$frames_per_eg \
    --egs.chunk-left-context=0 \
    --egs.chunk-right-context=0 \
    --egs.dir="$common_egs_dir" \
    --egs.opts="--frames-overlap-per-eg 0" \
    --cleanup.remove-egs=$remove_egs \
    --use-gpu=true \
    --reporting.email="$reporting_email" \
    --feat-dir=$train_data_dir \
    --tree-dir=$tree_dir \
    --lat-dir=exp/$train_lat \
    --dir=$dir  || exit 1;
fi

if [ $stage -le 16 ]; then
  utils/lang/check_phones_compatible.sh \
    data/lang_test_tgpr/phones.txt $lang/phones.txt
  utils/mkgraph.sh \
    --self-loop-scale 1.0 data/lang_test_tgpr \
    $tree_dir $tree_dir/graph_tgpr || exit 1;

  utils/lang/check_phones_compatible.sh \
    data/lang_test_bd_tgpr/phones.txt $lang/phones.txt
  utils/mkgraph.sh \
    --self-loop-scale 1.0 data/lang_test_bd_tgpr \
    $tree_dir $tree_dir/graph_bd_tgpr || exit 1;
fi

if [ $stage -le 17 ]; then
  frames_per_chunk=$(echo $frames_per_eg | cut -d, -f1)
  rm $dir/.error 2>/dev/null || true
  for data in $test_sets; do
    (
      data_affix=$(echo $data | sed s/test_//)
      nspk=$(wc -l <data/${data}_hires/spk2utt)
      for lmtype in tgpr bd_tgpr; do
        steps/nnet3/decode.sh \
          --acwt 1.0 --post-decode-acwt 10.0 \
          --extra-left-context 0 --extra-right-context 0 \
          --extra-left-context-initial 0 \
          --extra-right-context-final 0 \
          --frames-per-chunk $frames_per_chunk \
          --nj $nspk --cmd "$decode_cmd"  --num-threads 4 \
          $tree_dir/graph_${lmtype} data/${data}_hires ${dir}/decode_${lmtype}_${data_affix} || exit 1
      done
      steps/lmrescore.sh \
        --self-loop-scale 1.0 \
        --cmd "$decode_cmd" data/lang_test_{tgpr,tg} \
        data/${data}_hires ${dir}/decode_{tgpr,tg}_${data_affix} || exit 1
      steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" \
        data/lang_test_bd_{tgpr,fgconst} \
       data/${data}_hires ${dir}/decode_${lmtype}_${data_affix}{,_fg} || exit 1
    ) || touch $dir/.error &
  done
  wait
  [ -f $dir/.error ] && echo "$0: there was a problem while decoding" && exit 1
fi

#decode_nj=30
#if [ $stage -le 18 ]; then
#  rm $dir/.error 2>/dev/null || true
#  for decode_set in train_dev eval2000 $maybe_rt03; do
#      (
#    for lmtype in tgpr bd_tgpr; do
#      steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 \
#          --nj $decode_nj --cmd "queue.pl" \
#          $tree_dir/graph_${lmtype} data/${decode_set}_hires \
#          $dir/decode_${lmtype}_${decode_set} || exit 1;
#    done
#      if $has_fisher; then
#          steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" \
#            data/lang_test_bd_{tgpr,fgconst} data/${decode_set}_hires \
#            $dir/decode_bd_tgpr_${decode_set}{,_fg} || exit 1;
#      fi
#      ) || touch $dir/.error &
#  done
#  wait
#  if [ -f $dir/.error ]; then
#    echo "$0: something went wrong in decoding"
#    exit 1
#  fi
#fi

#if [ $stage -le 19 ]; then
#  rm $dir/.error 2>/dev/null || true
#  for x in eval2000; do
#    for n in noise reverb music babble; do
#      decode_set=${x}_${n}
#      dataset=$decode_set
#      for lmtype in tgpr bd_tgpr; do
#        steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 \
#          --nj $decode_nj --cmd "$decode_cmd" \
#          $tree_dir/graph_${lmtype} data/${decode_set}_hires \
#          $dir/decode_${lmtype}_${decode_set} || exit 1;
#      done
#      if $has_fisher; then
#          steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" \
#            data/lang_test_bd_{tgpr,fgconst} data/${decode_set}_hires \
#            $dir/decode_bd_tgpr_${decode_set}{,_fg} || exit 1;
#      fi
#    done
#  done
#  if [ -f $dir/.error ]; then
#    echo "$0: something went wrong in decoding"
#    exit 1
#  fi
#fi

#if [ $stage -le 20 ]; then
#  rm $dir/.error 2>/dev/null || true
#  for decode_set in ihm_eval_orig ihm_eval sdm1_eval_orig sdm1_eval dev_aspire; do
#    for lmtype in tgpr bd_tgpr; do
#      steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 \
#        --nj 10 --cmd "$decode_cmd" \
#        $tree_dir/graph_${lmtype} data/${decode_set}_hires \
#        $dir/decode_${lmtype}_${decode_set} || exit 1;
#    done
#  done
#  if [ -f $dir/.error ]; then
#    echo "$0: something went wrong in decoding"
#    exit 1
#  fi
#fi
#exit 0;
