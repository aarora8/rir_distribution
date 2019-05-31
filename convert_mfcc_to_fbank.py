import os
import sys
import random
import argparse

import numpy as np
import kaldi_io

#matplotlib inline
#import IPython.display
import matplotlib.pyplot as plt

sys.path.insert(0, 'steps')
import libs.common as common_lib

def get_args():
    parser = argparse.ArgumentParser(description="Apply idct")
    parser.add_argument('--prefix', type=str, default=None, help='prefix to be applied to fbank')
    parser.add_argument("inp_feats_scp", help='inp_feats_scp on top of which mask will be applied')
    parser.add_argument("out_feats_ark", help='out_feats_ark where masked features are saved')

    print(' '.join(sys.argv))
    args = parser.parse_args()
    args = check_args(args)

    return args


def check_args(args):
    ark_dir = os.path.dirname(args.out_feats_ark)
    print(ark_dir)
    if not os.path.isdir(ark_dir):
        os.makedirs(ark_dir)

    return args

def apply_idct(feats):
    num_mel = np.shape(feats)[-1]
    idct_mat = common_lib.compute_idct_matrix(
            num_mel, num_mel, 22.0)
    dct_mat = common_lib.compute_dct_matrix(
            num_mel, num_mel, 22.0)
    #print("  ___ start ___  ")
    #print(np.shape(feats))
    #print(np.shape(idct_mat))
    fbank = feats.dot(idct_mat)
    mfcc = fbank.dot(dct_mat)
    fbank2 = mfcc.dot(idct_mat)
    #print(np.shape(fbank))
    return fbank2


def pretty_spectrogram(specgram, thresh=2, start_frame=0, end_frame=-1):
    specgram[specgram < -thresh] = -thresh
    if end_frame == -1:
        end_frame = len(specgram)
    if end_frame > len(specgram):
        end_frame = len(specgram)
    if start_frame > len(specgram):
        start_frame = 0
    specgram = specgram[start_frame:end_frame, :]
    
    return specgram


def main():
    args = get_args()
    inp_feats_scp = args.inp_feats_scp
    out_feats_ark = args.out_feats_ark
    prefix = args.prefix
    ark_scp_output='ark:| copy-feats --compress=true ark:- ark,scp:{p}.ark,{p}.scp'.format(
                                                p=out_feats_ark)
    with kaldi_io.open_or_fd(ark_scp_output,'wb') as f:
        for utt, feats in kaldi_io.read_mat_scp(inp_feats_scp):
            # Get a masked copy of the feats
            feats_freq_masked = apply_idct(feats)
            #target = pretty_spectrogram(target, start_frame=start_fr, end_frame=end_fr)
            ## Plot predicted spectrograms
            #fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 4))
            #cax = ax.matshow(np.transpose(target), interpolation='nearest', aspect='auto', cmap=plt.cm.afmhot, origin='lower')
            #fig.colorbar(cax)
            #plt.title('Original Spectrogram')

            if prefix is not None:
                utt = '{p}-{u}'.format(p=prefix, u=utt)
            np.save('ark_check2/{u}.npy'.format(u=utt), feats_freq_masked)
            #kaldi_io.write_mat(f, feats_freq_masked, key=utt)


if __name__ == "__main__":
    main()


