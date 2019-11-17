% Script to start target generation for specified data sets. Targets are
% composed of the localization azimuth with respect to the head orientation for
% all conditions.

clear
close all
clc
addpath('tools')

%% Set paths and files

% Data set directory (containing earSignals)
stats_dir = {'../data_set/exp1/analysis/stats/',...
             '../data_set/exp2/analysis/stats/'};
 
% Directory to export files to           
export_dir = {'../generated/exp1/targets/',...
              '../generated/exp2/targets/'};

%% Compute and save
for i=1:length(stats_dir)
    calc_loc_az_wrt_head_ori(stats_dir{i},export_dir{i})
end