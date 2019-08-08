clear
close all
clc

%% Set parameters and define paths/files
%
% Stimulus length to use in seconds
stimulus_len = 1;
% Folder name of the data set to use (in dataset_path)
set = 'exp1';

% Define paths
export_path = fullfile('generated',set,'earSignals');
dataset_path = fullfile(fileparts(mfilename('fullpath')),'data_set',set);
ir_path = fullfile(dataset_path,'brs');
stimuli_path = fullfile(dataset_path,'stimuli');

% Create folder if inexistent
if ~exist(export_path,'dir'); mkdir(export_path); end

% Obtain all file names and number of files
ir_files = dir(ir_path);
file_flags = ~[ir_files.isdir];
ir_files = ir_files(file_flags);
num = 1:length(ir_files);

stimulus_files = dir(stimuli_path);
file_flags = ~[stimulus_files.isdir];
stimulus_files = stimulus_files(file_flags);

%% Load stimulus signal
%
[stimulus, fs] = audioread(fullfile(stimuli_path,stimulus_files.name));
% Extract one second and remove zeros 
stimulus = stimulus(1:stimulus_len*fs);
stimulus(stimulus==0) = [];
load('generated/wn.mat');
stimulus = wn;

%% Obtain ear signals
%
% Repeat for each brs file
for i=1%num
    % Load ir signal
    ir = audioread(fullfile(ir_path,ir_files(i).name));
    
    earSignals = zeros(length(stimulus)+length(ir)-1,720);
    % Generate ear signals for each angle (360) by convolution
    for j=1:720
        earSignals(:,j) = conv(stimulus,ir(:,j));
    end
    % Save
    [~,filename,~] = fileparts(ir_files(i).name);
    filename = strcat('earSignals_',filename,'.mat');
    filename = fullfile(export_path,filename);
    save(filename,'earSignals','fs');
end
