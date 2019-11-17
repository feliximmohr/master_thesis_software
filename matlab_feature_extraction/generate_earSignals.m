function generate_earSignals(dataset_dir,export_dir,stimulus_file,stimulus_len)
%GEN_EARSIGNALS generates binaural ear signals for each head rotation angle by
% convolving a stimulus signal with binaural impulse responses. The results
% are stored in one .mat file corresponding to one impulse response/condition.
% To speed up computation, the Parallel Computing Toolbox of MATLAB is used,
% as the computation of the ear signals is independent.
%
%   Usage: 
%   generate_earSignals(dataset_dir,export_dir,stimulus_file,stimulus_len)
%
%   Input parameters:
%       dataset_dir     - path to data set directory
%       export_dir      - path to directory to save the computation outcome
%       stimulus_file   - path to either .wav or .mat file containing stimulus
%                         signal
%       stimulus_len    - length to optionally truncate the stimulus signal to

%% Set parameters and define paths/files

% Define paths
ir_dir = fullfile(dataset_dir,'brs');
stimuli_dir = fullfile(dataset_dir,'stimuli');
dataset_name = strsplit(dataset_dir, '/');
dataset_name = dataset_name{end};

% Create export folder if inexistent
if ~exist(export_dir,'dir'); mkdir(export_dir); end

% Obtain all file names and number of files
[ir_files, num] = get_filelist(ir_dir);
% Restruct filenames to common standard
filelist_out = reformat_filename(ir_files,dataset_name,'earSignals');

% Define stimulus file in case not specified as input argument
if nargin < 3
    stimulus_file = get_filelist(stimuli_dir);
    stimulus_file = fullfile(stimuli_dir,stimulus_file{1});
end
[~,~,stimulus_file_ext] = fileparts(stimulus_file);

if nargin < 4; stimulus_len = 1; end

%% Load stimulus signal

% Load either from .wav or .mat file
if strcmp(stimulus_file_ext,'wav')
    [stimulus, fs] = audioread(stimulus_file);
    % Extract specified length
    stimulus = stimulus(1:stimulus_len*fs);
else
    try
        load(stimulus_file,'stimulus','fs');
    catch
        error('Error occurred. Only .wav and .mat files allowed to load stimulus signal.')
    end 
end

%% Obtain ear signals

% Repeat for each brs file
parfor i=1:num
    % Load ir signal
    ir = audioread(fullfile(ir_dir,ir_files{i}));
    
    earSignals = zeros(length(stimulus)+length(ir)-1,720);
    % Generate ear signals for each angle (0-359) by convolution
    for j=1:720
        earSignals(:,j) = conv(stimulus,ir(:,j));
    end
    % Save
    filename = fullfile(export_dir, filelist_out{i});
    save_variables([filename,'.mat'],{'earSignals','fs'},{earSignals,fs});
end

end