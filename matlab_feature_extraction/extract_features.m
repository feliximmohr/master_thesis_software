function extract_features(requests,par,earSignal_dir,export_dir,output_type,trunc_idx,reformat_filename)
%EXTRACT_FEATURES uses the Two!Ears Auditory Front-End and its processors
% to calculate binaural features, such as ILD, ITD and IC from binaural ear
% signals and writes the computation results to files as specified.
%   #TODO: extended documentation
%
%   Usage: extract_features(requests,par,trunc_idx,dataset_dir,export_dir,output_type)
%
%   Input parameters:
%       requests    - cell array containing string of requested feature
%       par         - parameter structure for Two!Ears Auditory Front-End processor requests
%       trunc_idx   - index of last not truncated sample of each computed feature
%       dataset_dir - path to data set directory
%       export_dir  - path to directory to save the computation outcome
%       output_type - specify type of file to save (e.g. 'mat_array','table')
% 

if nargin < 7
    reformat_filename = 0;
end

%% Set paths and files
% 
dataset_name = strsplit(earSignal_dir, '/');
dataset_name = dataset_name{end-1};

% Create folder if inexistent
if ~exist(export_dir,'dir'); mkdir(export_dir); end

% Obtain all file names and number of files
earSignal_files = dir(earSignal_dir);
file_flags = ~[earSignal_files.isdir];
earSignal_files = earSignal_files(file_flags);
num = 1:length(earSignal_files);

% Optionally reformat filenames to common standard
[filelist{num}]=deal(earSignal_files.name);
if reformat_filename
    filelist = reformat_filename(filelist,dataset_name,'ild_itd_ic');
else
    filelist = strrep(filelist,'earSignals',strjoin(requests,'_'));
end

%% Processing
%
% Load a signal
load([earSignal_dir,filesep,earSignal_files(1).name],'earSignals', 'fs');
% Compute number of frames to preallocate outputs
inSize = size(earSignals);
ild_wSize = fs*par.ild_wSizeSec;    % Window duration in samples
ild_hSize = fs*par.ild_hSizeSec;    % Step size between windows in samples
cc_wSize = fs*par.cc_wSizeSec;
cc_hSize = fs*par.cc_hSizeSec;         
ild_nFrames = floor((inSize(1)-(ild_wSize-ild_hSize))/ild_hSize);
cc_nFrames = floor((inSize(1)-(cc_wSize-cc_hSize))/cc_hSize);
if nargin < 6
    trunc_idx = ild_nFrames;
end

fb_nChannels = par.fb_nChannels;
num_angles = inSize(2)/2;
num_inchannels = inSize(2);

% Execute for each input file (in a parfor loop to speed up computation)
parfor n = num
    
    % Preallocate outputs
    ild = zeros(fb_nChannels,ild_nFrames,num_angles);
    itd = zeros(fb_nChannels,cc_nFrames,num_angles);
    ic  = itd;
    
    % Load a signal
    mat = load([earSignal_dir,filesep,earSignal_files(n).name]);
    
    % Compute requested features for each stereo earSignal
    for i=1:2:num_inchannels
        % Create a data object based on the ear signals
        dObj = dataObject(mat.earSignals(:,i:i+1),mat.fs);

        % Create a manager
        mObj = manager(dObj,requests,par);

        % Request processing
        mObj.processSignal();
        
        % Save and optionally truncate requested data
        if any(strcmp(requests,'ild'))
            ild(:,1:trunc_idx,(i+1)/2) = dObj.ild{1}.Data(1:trunc_idx,:).';
        end
        if any(strcmp(requests,'itd'))
            itd(:,1:trunc_idx,(i+1)/2) = dObj.itd{1}.Data(1:trunc_idx,:).';
        end
        if any(strcmp(requests,'ic'))
            ic(:,1:trunc_idx,(i+1)/2)  = dObj.ic{1}.Data(1:trunc_idx,:).';
        end

    end
    
    % Save to file
    filename = fullfile(export_dir, filelist{n});
    
    if strcmp('mat_array',output_type)
        % save to .mat file
        FsHz = dObj.ild{1}.FsHz;
        cfHz = dObj.ic{1}.cfHz;
        save_variables([filename,'.mat'],['FsHz','cfHz',requests],[FsHz,cfHz,ild,itd,ic]);
    elseif strcmp('csv',output_type)
        % TODO: adapt to file renaming
        % save each ild/itd/ic to seperate files
%         for i=1:360
%             writematrix();
%             writematrix();
%             writematrix();
%         end
        
    elseif strcmp('table',output_type)
        % TODO: adapt to file renaming
        % untested
%         variables = {'cfHz', 'ILD', 'ITD', 'IC'};
%         for i=1:360
%             T = table(dObj.ic{1}.cfHz.', ild(:,:,i).', itd(:,:,i).', ic(:,:,i).', 'VariableNames', variables);
%             writetable(T, [filename, '.csv'])
%         end
    end
end

end

%% ===== Functions =======================================================

function save_variables(filename,var_names,variables)
%SAVE_VARIABLES saves variables under their respective names in a .mat
% file. This function prevents the MATLAB save function to fail an a parfor
% loop.
s = cell2struct(variables{1:length(var_names)},var_names);
save(filename, s)
end