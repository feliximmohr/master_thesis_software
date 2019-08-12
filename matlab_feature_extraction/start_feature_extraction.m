% Script to start feature extraction for specified data sets

clear
close all
clc
%% Set paths and files
% Specify output type ('mat_array', 'table')
output_type = 'mat_array';

dataset_dir = {'../data_set/exp1/',...
               '../data_set/exp2/'};
           
export_dir = fullfile(dataset_dir, 'features');

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

%% Compute and save
for i=1:length(dataset_dir)
    extract_features(requests,par,trunc_idx,dataset_dir{i},export_dir{i},output_type)
end