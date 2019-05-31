input_dir = '/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/smallroom/';
output_dir = '/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/smallroom_bs1/';
BitsPerSample = 16;
fs = 16000;
nyquist = fs/2;
gap = 450;
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
            if max(abs(bs_RIR)) < 1
                break
            end
        end
    end
    start_frequency_hz
    end_frequency_hz
    [utt,fs1] = audioread('/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/wav_files/utt.wav');
    y2 = conv(bs_RIR, utt);
    figure, spectrogram(y2,400,200,256,16000,'yaxis');
    wavfilename = strcat(output_dir, '/', directoryname, '/', txtfilename);
    audiowrite(wavfilename, bs_RIR, fs, 'BitsPerSample', BitsPerSample);
  end
end
