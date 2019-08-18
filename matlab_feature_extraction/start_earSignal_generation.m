% Script to start generation of binaura ear signals by convolution of
% stimulus signal with a set of binaural room impulse responses for
% specified data sets.

clear
close all
clc

addpath('tools')

%% Set paths and files
% Data set directory
dataset_dir = {'../data_set/exp1',...
               '../data_set/exp2'};
           
% Directory to export files to
export_dir = {'../generated/exp1/earSignals',...
              '../generated/exp2/earSignals'};
          
% Stimulus signal file
stimulus_file = '../generated/wn.mat';
% Stimulus length to use in seconds
stimulus_len = 1;

%% Compute and save
for i=1:length(dataset_dir)
    generate_earSignals(dataset_dir{i},export_dir{i},stimulus_file,stimulus_len);
end