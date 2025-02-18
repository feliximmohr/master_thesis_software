% Script to start feature extraction for specified data sets and parameters
% with the Auditory front-end of the Two!Ears Auditory Model 1.5.
% DOI: 10.5281/zenodo.1458420

clear
close all
clc
addpath('tools')

% Start Two!Ears Framework
addpath('TwoEars-1.5')
startTwoEars()
startAuditoryFrontEnd()

%% Set paths and files

% Data set directory (containing earSignals)
earSignal_dir = {'../generated/exp1/earSignals',...
                 '../generated/exp2/earSignals'};
 
% Directory to export files to           
export_dir = {'../generated/exp1/features',...
              '../generated/exp2/features'};

% Sample indices to truncate features to
start_idx = 31;
trunc_idx = 40;
%% Set parameters for ILD/ITD/IC computation

% Features to extract
requests = {'ild','itd','ic'};

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

%% Compute and save
for i=1:length(earSignal_dir)
    extract_features(requests,par,earSignal_dir{i},export_dir{i},...
        trunc_idx,start_idx)
end