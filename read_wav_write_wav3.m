input_dir = '/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/smallroom/';
output_dir = '/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/smallroom_bs1/';
BitsPerSample = 16;
fs = 16000;
nyquist = fs/2;
gap = 500;
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
    fileID = strcat(input_dir, '/', directoryname,'/', txtfilename);
    [RIR,fs] = audioread(fileID);
    PassbandFrequency = int16(2000 * rand);
    PassbandFrequency = PassbandFrequency + 5000;
    StopbandFrequency = PassbandFrequency + 500;
    PassbandFrequency = double(PassbandFrequency);
    StopbandFrequency = double(StopbandFrequency);
    StopbandFrequency_hp = int16(100 * rand) + 5;
    PassbandFrequency_hp = StopbandFrequency_hp + 100;
    PassbandFrequency_hp = double(PassbandFrequency_hp);
    StopbandFrequency_hp = double(StopbandFrequency_hp);
    while 1
        start_frequency = int16(mel_range(end) * rand);
        bandwidth = int16(gap * rand);
        end_frequency = start_frequency + bandwidth + 100;
        start_frequency = double(start_frequency);
        end_frequency = double(end_frequency);
        start_frequency_hz = 700*((exp(start_frequency/1127)-1));
        end_frequency_hz = 700*((exp(end_frequency/1127)-1));
        start_frequency_hz = double(int16(start_frequency_hz));
        end_frequency_hz = double(int16(end_frequency_hz));
        if end_frequency_hz < nyquist && start_frequency_hz > 0 && start_frequency_hz < end_frequency_hz
            break
        end
    end
    start_frequency_hz
    end_frequency_hz
    size(bsFilt.Coefficients)
    %bsFilt = designfilt('bandstopiir','FilterOrder',40,'HalfPowerFrequency1',start_frequency_hz,'HalfPowerFrequency2',end_frequency_hz, 'SampleRate',fs);
    bsFilt = designfilt('bandstopfir','FilterOrder',200,'CutoffFrequency1',start_frequency_hz,'CutoffFrequency2',end_frequency_hz,'SampleRate',fs);
    lpFilt = designfilt('lowpassfir','FilterOrder',100,'PassbandFrequency',PassbandFrequency,'StopbandFrequency',StopbandFrequency,'SampleRate',fs);
    hpFilt = designfilt('highpassfir','FilterOrder',100,'StopbandFrequency',StopbandFrequency_hp,'PassbandFrequency',PassbandFrequency_hp,'SampleRate',fs);
    [utt,fs1] = audioread('/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/wav_files/utt.wav');
    bs_RIR=filter(lpFilt,bsFilt.Coefficients);
    y2 = conv(bs_RIR, utt);
    figure, spectrogram(y2,400,200,256,16000,'yaxis');
    
%     bs_RIR = filter(bsFilt, RIR);
%     inputmode = int16(4*rand);
%     switch inputmode
%     case 1
%         bs_RIR=filter(lpFilt,bs_RIR);
%     case 2
%         bs_RIR=filter(hpFilt,bs_RIR);
%     case 3
%         bs_RIR=filter(lpFilt,bs_RIR);
%         bs_RIR=filter(hpFilt,bs_RIR);
%     end
%     wavfilename = strcat(output_dir, '/', directoryname, '/', txtfilename);
%     audiowrite(wavfilename, bs_RIR, fs, 'BitsPerSample', BitsPerSample);
  end
end
