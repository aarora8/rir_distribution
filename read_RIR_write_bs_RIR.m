input_dir = '/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/mediumroom_bs/';
output_dir = '/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/room_copy_specto';
BitsPerSample = 16;
fs = 16000;
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
    [utt,fs1] = audioread('/Users/ashisharora/Documents/MATLAB/kaldi_augmentation/wav_files/utt.wav');
    y2=conv(utt,RIR);
    wavfile_1 = strcat(output_dir, '/', directoryname, '/', filename, '.png');
    figure, spectrogram(y2,400,200,256,16000,'yaxis');
    title(filename);
    saveas(gcf,wavfile_1);
  end
end
