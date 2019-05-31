#!/bin/bash
# This script reads RIR in .wav format and writes it into RIR + band stop
# Usage: prep_sim_rirs.sh <output-dir>
# E.g. prep_sim_rirs.sh data/simulated_rir_largeroom

input_dir=$1
output_dir=$2
prefix="small-"       # prefix to the RIR id
sampling_rate=16000     # Sampling rate of the output RIR waveform
output_bit=16
mkdir -p $output_dir

cat >./genrir4.m <<EOF
output_dir = '$output_dir';
input_dir = '$input_dir';
BitsPerSample = $output_bit;
fs = $sampling_rate;
nyquist = fs/2;
gap = 950;
freq_range = 1:nyquist;
mel_range = 2595 * log10(1 + freq_range/700);
listing = dir(input_dir);
isub = [listing(:).isdir];
nameFolds = {listing(isub).name};
nameFolds(ismember(nameFolds,{'.','..'})) = [];
for i = 1:length(nameFolds)
  directorycell = nameFolds(i);
  directoryname = directorycell{1};
  list = dir(strcat(input_dir, '/', directoryname, '/*.wav'));
  mkdir(output_dir,directoryname)
  for j = 1:length(list)
    txtfilename = list(j).name;
    [filepath,filename,ext] = fileparts(list(j).name);
    while 1
        start_frequency = int16(mel_range(end) * rand);
        bandwidth = int16(gap * rand);
        bandwidth = bandwidth + 50; % BW between 50 to 500 mel
        end_frequency = start_frequency + bandwidth;
        start_frequency = double(start_frequency);
        end_frequency = double(end_frequency);
        start_frequency_hz = 700*((exp(start_frequency/1127)-1));
        end_frequency_hz = 700*((exp(end_frequency/1127)-1));
        start_frequency_hz = double(int16(start_frequency_hz));
        end_frequency_hz = double(int16(end_frequency_hz));
        if end_frequency_hz < nyquist && start_frequency_hz > 0 && start_frequency_hz < end_frequency_hz
            bsFilt = designfilt('bandstopfir','FilterOrder',200,'CutoffFrequency1',start_frequency_hz,'CutoffFrequency2',end_frequency_hz,'SampleRate',fs);
            bs_RIR = bsFilt.Coefficients;
            if max(abs(bs_RIR)) <= 1
                break
            end
        end
    end
    start_frequency_hz
    end_frequency_hz
    wavfilename = strcat(output_dir, '/', directoryname, '/', txtfilename);
    audiowrite(wavfilename, bs_RIR, fs, 'BitsPerSample', BitsPerSample);
  end
end
EOF
matlab -nosplash -nodesktop < ./genrir4.m
rm genrir4.m
