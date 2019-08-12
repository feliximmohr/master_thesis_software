function extract_features(requests,par,trunc_idx,dataset_dir,export_dir,output_type)
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

%% Set paths and files
% 
earSignal_dir = fullfile(dataset_dir, 'earSignals');
dataset_name = strsplit(dataset_dir, '/');
dataset_name = dataset_name{end-1};

% Create folder if inexistent
if ~exist(export_dir,'dir'); mkdir(export_dir); end

% Obtain all file names and number of files
earSignal_files = dir(earSignal_dir);
file_flags = ~[earSignal_files.isdir];
earSignal_files = earSignal_files(file_flags);
num = 1:length(earSignal_files);
% Restruct filenames to common standard
[filelist{num}]=deal(earSignal_files.name);
filelist = reformat_filename(filelist,dataset_name,'ild_itd_ic');

%% Processing
%
% Load a signal
load([earSignal_dir,filesep,earSignal_files(1).name],'earSignals');
% Preallocate outputs
inSize = size(earSignals);
ild_wSize = fs*ild_wSizeSec;    % Window duration in samples
ild_hSize = fs*ild_hSizeSec;    % Step size between windows in samples
cc_wSize = fs*cc_wSizeSec;
cc_hSize = fs*cc_hSizeSec;         
ild_nFrames = floor((inSize(1)-(ild_wSize-ild_hSize))/ild_hSize);
cc_nFrames = floor((inSize(1)-(cc_wSize-cc_hSize))/cc_hSize);

ild = zeros(fb_nChannels,ild_nFrames,inSize(2)/2);
itd = zeros(fb_nChannels,cc_nFrames,inSize(2)/2);
ic  = itd;

for n = 1%num
    % Load a signal
    load([earSignal_dir,filesep,earSignal_files(n).name],'earSignals');
    
    for i=1:2:inSize(2)
        % Create a data object based on the ear signals
        dObj = dataObject(earSignals(:,i:i+1),fs);

        % Create a manager
        mObj = manager(dObj,requests,par);

        % Request processing
        mObj.processSignal();
        
        % Save and optionally truncate data
        ild(:,1:trunc_idx,(i+1)/2) = dObj.ild{1}.Data(1:trunc_idx,:).';
        itd(:,1:trunc_idx,(i+1)/2) = dObj.itd{1}.Data(1:trunc_idx,:).';
        ic(:,1:trunc_idx,(i+1)/2)  = dObj.ic{1}.Data(1:trunc_idx,:).';

    end
    %% Save to file
    filename = fullfile(export_dir, filelist{n});
    
    if strcmp('mat_array',output_type)
        % save to .mat file
        FsHz = dObj.ild{1}.FsHz;
        cfHz = dObj.ic{1}.cfHz;
        save([filename,'.mat'],'ild','itd','ic','FsHz', 'cfHz');
    elseif strcmp('csv',output_type)
        % TODO: adapt to file renaming
        % save each ild/itd/ic to seperate files
        for i=1:360
            writematrix();
            writematrix();
            writematrix();
        end
        
    elseif strcmp('table',output_type)
        % TODO: adapt to file renaming
        % untested
        variables = {'cfHz', 'ILD', 'ITD', 'IC'};
        for i=1:360
            T = table(dObj.ic{1}.cfHz.', ild(:,:,i).', itd(:,:,i).', ic(:,:,i).', 'VariableNames', variables);
            writetable(T, [filename, '.csv'])
        end
    end
end

end