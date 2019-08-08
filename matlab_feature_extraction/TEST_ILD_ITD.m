%clear
close all
%clc


%% LOAD SIGNAL
% 
% 
% Audio path
audioPath = fullfile(fileparts(mfilename('fullpath')),'Test_signals');

% Load a signal
%load([audioPath,filesep,'earSignals_brs_win-max-rE_ord-13_pos-1(-0.00x_0.75y)_corrected.mat']);

% Create a data object based on the ear signals
dObj = dataObject(earSignals(:,89:90),fs);


%% PLACE REQUEST AND CONTROL PARAMETERS
% 
% 
% Request interaural level differences (ILDs)
requests = {'ild', 'itd', 'ic'};

% Parameters of the auditory filterbank processor
fb_type       = 'gammatone';
fb_lowFreqHz  = 80;
fb_highFreqHz = 8000;
fb_nChannels  = 32;  

% Parameters of innerhaircell processor
ihc_method    = 'dau';

% Parameters of ILD and CC processor
ild_wSizeSec  = 0.02;
ild_hSizeSec  = 0.01;
ild_wname     = 'hann';

% Summary of parameters 
par = genParStruct('fb_type',fb_type,'fb_lowFreqHz',fb_lowFreqHz,...
                   'fb_highFreqHz',fb_highFreqHz,'fb_nChannels',fb_nChannels,...
                   'ihc_method',ihc_method,'ild_wSizeSec',ild_wSizeSec,...
                   'ild_hSizeSec',ild_hSizeSec,'ild_wname',ild_wname,...
                   'cc_wSizeSec', ild_wSizeSec, 'cc_hSizeSec', ild_hSizeSec, ...
                   'cc_wname', ild_wname); 
               
               
%% PERFORM PROCESSING
% 
% 
% Create a manager
mObj = manager(dObj,requests,par);

% Request processing
mObj.processSignal();


%% PLOT RESULTS
% 
% 
% Plot the original ear signal
dObj.plot([],[],'bGray',1,'decimateRatio',3,'bSignal',1);
ylim([-1.25 1.25]);

% Plot ILDs
dObj.ild{1}.plot;
title('ILD')

% Plot ITDs
dObj.itd{1}.plot;
title('ITD')

% Plot ICs
dObj.ic{1}.plot;
title('IC')
