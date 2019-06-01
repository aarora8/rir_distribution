import os
import sys
import random
import argparse

import numpy as np
import kaldi_io
sys.path.insert(0, 'steps')
import libs.common as common_lib

def get_args():
    parser = argparse.ArgumentParser(description="Apply idct")
    parser.add_argument("inp_feats_scp", help='inp_feats_scp on top of which mask will be applied')
    parser.add_argument("out_feats_ark", help='out_feats_ark where masked features are saved')
    args = parser.parse_args()
    return args


def convert_mfcc_to_fbank(feats):
    num_mel = np.shape(feats)[-1]
    idct_mat = common_lib.compute_idct_matrix(
            num_mel, num_mel, 22.0)
    idct_mat2 = np.transpose(idct_mat)
    fbank = feats.dot(idct_mat2)
    return fbank


def convert_fbank_to_mfcc(feats):
    num_mel = np.shape(feats)[-1]
    dct_mat = common_lib.compute_dct_matrix(
            num_mel, num_mel, 22.0)
    mfcc = feats.dot(dct_mat)
    return mfcc


def main():
    args = get_args()
    inp_feats_scp = args.inp_feats_scp
    out_feats_ark = args.out_feats_ark
    ark_scp_output='ark:| copy-feats --compress=true ark:- ark,scp:{p}.ark,{p}.scp'.format(
                                                p=out_feats_ark)
    with kaldi_io.open_or_fd(ark_scp_output,'wb') as f:
        for utt, feats in kaldi_io.read_mat_scp(inp_feats_scp):
            fbank = convert_fbank_to_mfcc(feats)
            np.save('ark_check4/{u}.npy'.format(u=utt), fbank)
            kaldi_io.write_mat(f, fbank, key=utt)


if __name__ == "__main__":
    main()


