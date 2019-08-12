function gen_earSignals(dataset_dir,export_dir,stimulus_file,stimulus_len)
%GEN_EARSIGNALS generates binaural ear signals for head rotation angle by
% convolving a stimulus signal with binaural room impulse responses.
%   #TODO: extended documentation
%
%   Usage: gen_earSignals(dataset_dir,export_dir,stimulus_file)
%
%   Input parameters:
%       dataset_dir     - path to data set directory
%       export_dir      - path to directory to save the computation outcome
%       stimulus_file   - path to either .wav or .mat file containing
%                         stimulus signal
%

%% Set parameters and define paths/files
%

% Define paths
ir_dir = fullfile(dataset_dir,'brs');
stimuli_dir = fullfile(dataset_dir,'stimuli');
dataset_name = strsplit(dataset_dir, '/');
dataset_name = dataset_name{end-1};

% Create folder if inexistent
if ~exist(export_dir,'dir'); mkdir(export_dir); end

% Obtain all file names and number of files
ir_files = dir(ir_dir);
file_flags = ~[ir_files.isdir];
ir_files = ir_files(file_flags);
num = 1:length(ir_files);
% Restruct filenames to common standard
[filelist{num}]=deal(ir_files.name);
filelist = reformat_filename(filelist,dataset_name,'ild_itd_ic');

% Define stimulus file in case not specified as input argument
if nargin < 3
    stimulus_file = dir(stimuli_dir);
    file_flags = ~[stimulus_file.isdir];
    stimulus_file = stimulus_file(file_flags);
    stimulus_file = fullfile(stimuli_dir,stimulus_file.name);
end
[~,~,stimulus_file_ext] = fileparts(stimulus_file);

%% Load stimulus signal
% Load either from .wav or .mat file
if strcmp(stimulus_file_ext,'wav')
    [stimulus, fs] = audioread(stimulus_file);
    % Extract one second 
    stimulus = stimulus(1:stimulus_len*fs);
else
    try
        load(stimulus_file,'stimulus');
    catch
        error('Error occurred. Only .wav and .mat files allowed to load stimulus signal.')
    end 
end

%% Obtain ear signals
%
% Repeat for each brs file
for i=1%num
    % Load ir signal
    ir = audioread(fullfile(ir_dir,ir_files(i).name));
    
    earSignals = zeros(length(stimulus)+length(ir)-1,720);
    % Generate ear signals for each angle (0-359) by convolution
    for j=1:720
        earSignals(:,j) = conv(stimulus,ir(:,j));
    end
    % Save
    filename = fullfile(export_dir, filelist{n});
    save(filename,'earSignals','fs');
end

end