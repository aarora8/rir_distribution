import os
import sys
import random
import argparse

import numpy as np
import kaldi_io
import matplotlib.pyplot as plt
sys.path.insert(0, 'steps')

def get_args():
    parser = argparse.ArgumentParser(description="Apply idct")
    parser.add_argument('--prefix', type=str, default=None, help='prefix to be applied to fbank')
    parser.add_argument("inp_feats_scp", help='inp_feats_scp on top of which mask will be applied')
    parser.add_argument("out_feats_ark", help='out_feats_ark where masked features are saved')

    args = parser.parse_args()
    return args

def main():
    args = get_args()
    inp_feats_scp = args.inp_feats_scp
    out_feats_ark = args.out_feats_ark
    prefix = args.prefix
    for utt, feats in kaldi_io.read_mat_scp(inp_feats_scp):
        if prefix is not None:
            utt = '{p}-{u}'.format(p=prefix, u=utt)
        np.save('{u}.npy'.format(u=utt), feats)


if __name__ == "__main__":
    main()
