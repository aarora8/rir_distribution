output_dir = '/Users/ashisharora/mediumroom/room_copy_copy';
input_dir = '/Users/ashisharora/mediumroom/room_copy';
BitsPerSample = 16;
fs = 16000;
nyquist = fs/4;
gap = 1000;
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
    while 1
        start_frequency = int16(nyquist * rand);
        bandwidth = int16(gap * rand);
        start_frequency = start_frequency - 1000;
        end_frequency = start_frequency + bandwidth;
        start_frequency = double(start_frequency);
        end_frequency = double(end_frequency);
        if end_frequency <= nyquist && start_frequency >= 0
            break
        end
    end
%     start_frequency
%     end_frequency
    bsFilt = designfilt('bandstopiir','FilterOrder',40,'HalfPowerFrequency1',start_frequency,'HalfPowerFrequency2',end_frequency, 'SampleRate',16000);
    bs_RIR = filter(bsFilt, RIR);
    wavfilename = strcat(output_dir, '/', directoryname, '/', txtfilename);
    audiowrite(wavfilename, bs_RIR, fs, 'BitsPerSample', BitsPerSample);
  end
end
