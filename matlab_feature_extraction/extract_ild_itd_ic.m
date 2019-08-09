clear
close all
clc

% Specify output type ('mat_array', 'table')
output_type = 'mat_array';

%% Set parameters for ILD/ITD/IC computation
%
% Features to extract
requests = {'ild', 'itd', 'ic'};

% Parameters of the auditory filterbank processor
fb_type       = 'gammatone';
fb_lowFreqHz  = 80;
fb_highFreqHz = 8000;
fb_nChannels  = 32;  

% Parameters of innerhaircell processor
ihc_method    = 'dau';

% Parameters of ILD processor
ild_wSizeSec  = 0.02; 
ild_hSizeSec  = 0.01;
ild_wname     = 'hann';

% Parameters of crosscorrelation processor for ITD/IC
cc_wSizeSec   = 0.02;
cc_hSizeSec   = 0.01;
cc_wname      = 'hann';

% Summary of parameters 
par = genParStruct('fb_type',fb_type,'fb_lowFreqHz',fb_lowFreqHz,...
                   'fb_highFreqHz',fb_highFreqHz,'fb_nChannels',fb_nChannels,...
                   'ihc_method',ihc_method,'ild_wSizeSec',ild_wSizeSec,...
                   'ild_hSizeSec',ild_hSizeSec,'ild_wname',ild_wname,...
                   'cc_wSizeSec',cc_wSizeSec,'cc_hSizeSec',cc_hSizeSec,...
                   'cc_wname',cc_wname);

%% Set paths and files
% 
% Data set name
set = 'exp1';

earSignal_path = fullfile(fileparts(mfilename('fullpath')),'../generated', set, 'earSignals');
export_path = fullfile(earSignal_path,'..', 'features' );

% Create folder if inexistent
if ~exist(export_path,'dir'); mkdir(export_path); end

% Obtain all file names and number of files
earSignal_files = dir(earSignal_path);
file_flags = ~[earSignal_files.isdir];
earSignal_files = earSignal_files(file_flags);
num = 1:length(earSignal_files);

%% Processing
%
% Load a signal
load([earSignal_path,filesep,earSignal_files(1).name]);
% Preallocate outputs
inSize = size(earSignals);
ild_wSize = fs*ild_wSizeSec;    % Window duration in samples
ild_hSize = fs*ild_hSizeSec;    % Step size between windows in samples
cc_wSize = fs*cc_wSizeSec;
cc_hSize = fs*cc_hSizeSec;         
ild_nFrames = floor((inSize(1)-(ild_wSize-ild_hSize))/ild_hSize);
cc_nFrames = floor((inSize(1)-(cc_wSize-cc_hSize))/cc_hSize);

ild = zeros(ild_nFrames,fb_nChannels,inSize(2)/2);
itd = zeros(cc_nFrames,fb_nChannels,inSize(2)/2);
ic  = itd;

for n = 1%num
    % Load a signal
    load([earSignal_path,filesep,earSignal_files(n).name]);
    
    for i=1:2:inSize(2)
        % Create a data object based on the ear signals
        dObj = dataObject(earSignals(:,i:i+1),fs);

        % Create a manager
        mObj = manager(dObj,requests,par);

        % Request processing
        mObj.processSignal();

        %dObj.ild{1}.plot;

        ild(:,:,(i+1)/2) = dObj.ild{1}.Data(:).';
        itd(:,:,(i+1)/2) = dObj.itd{1}.Data(:).';
        ic(:,:,(i+1)/2)  = dObj.ic{1}.Data(:).';

    end
    %% Save to file
    [~,filename,~] = fileparts(earSignal_files(n).name);
    filename = strrep(filename,'earSignals','ild_itd_ic');
    %filename = strcat('ild_itd_ic_',earSignal_files(n).name);
    filename = fullfile(export_path, filename);
    
    if strcmp('mat_array',output_type)
        % save to .mat file
        FsHz = dObj.ild{1}.FsHz;
        cfHz = dObj.ic{1}.cfHz;
        save([filename,'.mat'],'ild','itd','ic','FsHz', 'cfHz');
    elseif strcmp('seperate_csv',output_type)
        % save each ild/itd/ic to seperate files
        for i=1:360
            writematrix();
            writematrix();
            writematrix();
        end
        
    elseif strcmp('table',output_type)
        % untested
        variables = {'cfHz', 'ILD', 'ITD', 'IC'};
        for i=1:360
            T = table(dObj.ic{1}.cfHz.', ild(:,:,i).', itd(:,:,i).', ic(:,:,i).', 'VariableNames', variables);
            writetable(T, [filename, '.csv'])
        end
    end
end

%% Plot for testing
% 
% 
% Plot the original ear signal
%dObj.plot([],[],'bGray',1,'decimateRatio',3,'bSignal',1);
%ylim([-1.25 1.25]);

% Plot ILDs
%dObj.ild{1}.plot;
%title('ILD')
