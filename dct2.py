import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def pretty_spectrogram(specgram, thresh=0, start_frame=0, end_frame=-1):
    specgram[specgram < 0] = 0
    if end_frame == -1:
        end_frame = len(specgram)
    if end_frame > len(specgram):
        end_frame = len(specgram)
    if start_frame > len(specgram):
        start_frame = 0
    specgram = specgram[start_frame:end_frame, :]

    return specgram


target = np.load("/Users/ashisharora/fbank_feats/reverb1-011c0201.npy")
target = pretty_spectrogram(target)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 4))
cax = ax.matshow(np.transpose(target), interpolation='nearest', aspect='auto', origin='lower')
fig.colorbar(cax)
plt.title('reverb1-011c0201')
fig.savefig('plot2d1.png')
