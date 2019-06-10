# rir_distribution
preserve model: steps/nnet3/chain/train.py
steps/libs/nnet3/train/common.py

cat combine.cegs | nnet3-chain-copy-egs ark:- ark,scp:combine1.cegs,combine1.scp

cat cegs.1.ark | nnet3-chain-copy-egs ark:- ark,scp:combine2.cegs,combine2.scp

cat cegs.*.ark | nnet3-chain-copy-egs ark:- ark,scp:combine3.cegs,combine3.scp

cat uttlist | cut -d'-' -f1 | sort | uniq | head

cat utt2spk | awk -v p=reverb '{printf("%s%s %s\n", p, $1, $1);}' > utt2uniq

$cmd JOB=1:20 exp/tri4_lats_nodup_aug/log/copy_out_lat.JOB.log   lattice-copy --write-compact=true "ark:gunzip -c exp/tri4_lats_nodup_aug/lat.JOB.gz |" ark,scp:exp/tri4_lats_nodup_aug/lat_tmp.JOB.ark,exp/tri4_lats_nodup_aug/lat_tmp.JOB.scp


