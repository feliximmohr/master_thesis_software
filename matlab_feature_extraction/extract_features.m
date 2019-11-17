function extract_features(requests,par,earSignal_dir,export_dir,trunc_idx,start_idx,reformat_filename)
%EXTRACT_FEATURES uses the Two!Ears Auditory Front-End and its processors
% to calculate binaural features, such as ILD, ITD and IC from binaural ear
% signals and writes the computation results to files as specified.
%
% Requires Two!Ears Auditory Model (Tested with version 1.5).
% DOI: 10.5281/zenodo.1458420
%
%   Usage: extract_features(requests,par,earSignal_dir,export_dir,trunc_idx,start_idx,reformat_filename)
%
%   Input parameters:
%       requests          - cell array containing string of requested feature
%       par               - parameter structure for Two!Ears Auditory Front-End
%                           processor requests
%       earSignal_dir     - path to ear signal directory
%       export_dir        - path to directory to save the computation outcome
%       trunc_idx         - index of last not truncated sample of each computed
%                           feature
%       start _idx        - index of first sample
%       reformat_filename - boolean for optionally reformatting the filenames

if nargin < 7
    reformat_filename = 0;
elseif nargin < 6
    start_idx = 1;
end

%% Set paths and files
% 
dataset_name = strsplit(earSignal_dir, '/');
dataset_name = dataset_name{end-1};

% Create export folder if inexistent
if ~exist(export_dir,'dir'); mkdir(export_dir); end

% Obtain all file names and number of files
[earSignal_files, num] = get_filelist(earSignal_dir);

% Optionally reformat filenames to common standard
if reformat_filename
    filelist_out = reformat_filename(earSignal_files,dataset_name,'ild_itd_ic');
else
    filelist_out = strrep(earSignal_files,'earSignals',strjoin(requests,'_'));
end

%% Processing
%
% Load a signal
load([earSignal_dir,filesep,earSignal_files{1}],'earSignals', 'fs');
% Compute number of frames to preallocate outputs
inSize = size(earSignals);
if nargin < 5
    ild_wSize = fs*par.ild_wSizeSec;    % Window duration in samples
    ild_hSize = fs*par.ild_hSizeSec;    % Step size between windows in samples
    cc_wSize = fs*par.cc_wSizeSec;
    cc_hSize = fs*par.cc_hSizeSec;         
    ild_nFrames = floor((inSize(1)-(ild_wSize-ild_hSize))/ild_hSize);
    cc_nFrames = floor((inSize(1)-(cc_wSize-cc_hSize))/cc_hSize);
    trunc_idx = ild_nFrames;
else
    ild_nFrames = trunc_idx - start_idx + 1;
    cc_nFrames = trunc_idx - start_idx + 1;
end

fb_nChannels = par.fb_nChannels;
nAngles = inSize(2)/2;
nInChannels = inSize(2);

% Execute for each input file (in a parfor loop to speed up computation)
parfor n = 1:num
    
    % Preallocate outputs
    ild = zeros(fb_nChannels,ild_nFrames,nAngles);
    itd = zeros(fb_nChannels,cc_nFrames,nAngles);
    ic  = itd;
    
    % Load a signal
    mat = load([earSignal_dir,filesep,earSignal_files{n}]);
    
    % Compute requested features for each stereo earSignal
    for i=1:2:nInChannels
        % Create a data object based on the ear signals
        dObj = dataObject(mat.earSignals(:,i:i+1),mat.fs);

        % Create a manager
        mObj = manager(dObj,requests,par);

        % Request processing
        mObj.processSignal();
        
        % Save and optionally truncate requested data
        if any(strcmp(requests,'ild'))
            ild(:,:,(i+1)/2) = dObj.ild{1}.Data(start_idx:trunc_idx,:).';
        end
        if any(strcmp(requests,'itd'))
            itd(:,:,(i+1)/2) = dObj.itd{1}.Data(start_idx:trunc_idx,:).';
        end
        if any(strcmp(requests,'ic'))
            ic(:,:,(i+1)/2)  = dObj.ic{1}.Data(start_idx:trunc_idx,:).';
        end

    end
    
    % Save to mat file
    filename = fullfile(export_dir, filelist_out{n});
    par_save = par.getHashObjects;
    par_save.nFrames = ild_nFrames;
    par_save.nAngles = nAngles;
    par_save.feature_size = [fb_nChannels ild_nFrames nAngles];
    par_save.FsHz = dObj.ild{1}.FsHz;
    par_save.requests = requests;
    par_save.cfHz = dObj.ic{1}.cfHz;
    par_save.cfHz = dObj.ic{1}.cfHz;
    save_variables(filename,...
        ['par_save','requests',requests],...
        {par_save,requests,ild,itd,ic});     
end

end