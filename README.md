# rir_distribution
preserve model: steps/nnet3/chain/train.py
steps/libs/nnet3/train/common.py

cat combine.cegs | nnet3-chain-copy-egs ark:- ark,scp:combine1.cegs,combine1.scp

cat cegs.1.ark | nnet3-chain-copy-egs ark:- ark,scp:combine2.cegs,combine2.scp
