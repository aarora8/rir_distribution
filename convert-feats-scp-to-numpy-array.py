import os
import sys
import kaldi_io
import numpy as np


#feats_scp = 'feats_mfcc_hires.scp'
feats_scp = 'feats_mfcc_hires_clean2.scp'
#feats_scp = 'feats_fbank.scp'
os.makedirs('hires_array', exist_ok=True)

for k,v in kaldi_io.read_mat_scp(feats_scp):
    np.save('hires_array/{u}.npy'.format(u=k), v)

