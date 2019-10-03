% Script to create tubular data structure from existing files
%TODO: extended documentation

clear
close all
clc
addpath('tools');

dataset_dir = {
             '/media/feliximmohr/Storage/master_thesis/generated/exp1/'
             '/media/feliximmohr/Storage/master_thesis/generated/exp2/'};

export_dir = '/media/feliximmohr/Storage/master_thesis/generated/database/raw/';

% Define metadata
% Listening positions
x = [0.00; 0.50; 1.00; 0.00; 0.50; 1.00; 1.25;  0.00;  0.50;  1.00]*(-1);
y = [0.75; 0.75; 0.75; 0.00; 0.00; 0.00; 0.00; -0.75; -0.75; -0.75];
% SFS methods
sfs_method = {
            'NFCHOA_M006'
            'NFCHOA_M013'
            'NFCHOA_M027'
            'NFCHOA_R006'
            'NFCHOA_R013'
            'NFCHOA_R027'
            'NFCHOA_R300'
            'LWFS-SBL_M003'
            'LWFS-SBL_M027'
            'LWFS-SBL_R003'
            'LWFS-SBL_R027'
            'LWFS-VSS_r15'
            'LWFS-VSS_r30'
            'LWFS-VSS_r45'
            'WFS'                
                };
% Reproduction setup
setup = {'circular_nls0056_dvs3.00'};
% Number of subjects (listeners)
n_subjects = 20;

%% Initialization

% Get all files and total number of files
n_files = 0;
feature_filelist = [];
target_filelist = [];
for i=1:size(dataset_dir,1)
    % Define directories
    features_dir = [dataset_dir{i},'features/'];
    targets_dir  = [dataset_dir{i},'targets/'];
    % Get filelist per specified dataset
    [feature_files,num] = get_filelist(features_dir);
    [target_files,~] = get_filelist(targets_dir);
    feature_files = fullfile(features_dir,feature_files);
    target_files = fullfile(targets_dir,target_files);
    % Create list of all filenames across datasets
    feature_filelist = [feature_filelist,feature_files];
    target_filelist = [target_filelist,target_files];
    % Total number of files (equals number of conditions*positions)
    n_files = n_files + num;
end
% Sort filelists
feature_filelist = sort(feature_filelist);
target_filelist = sort(target_filelist);
    
% Load metadata
par = load(feature_filelist{1},'par_save');
par = par.par_save;

% Initialize
n_fb_channel = par.fb_nChannels;
n_frames_file = par.nFrames*par.nAngles;
n_features = length(par.requests)*n_fb_channel;
feature_data = zeros(n_frames_file*n_files, n_features);
target_data = zeros(n_files*par.nAngles,n_subjects);

global_id = uint32(0:n_frames_file*n_files*n_subjects-1).';
p_id = zeros(1, n_frames_file*n_files, 'uint8');
c_id = zeros(1, n_frames_file*n_files, 'uint8');
s_id = uint8(1:n_subjects).';
s_id = repmat(s_id,n_frames_file*n_files,1);

%% Processing

% Do for each file
for j = 1:n_files
    % Load each file
    features = load(feature_filelist{j});
    targets = load(target_filelist{j});

    % Reshape features to table structure
    [ild,itd,ic] = deal([]);
    if any(strcmp(par.requests,'ild'))
        ild = reshape(features.ild,n_fb_channel,n_frames_file).';
    end
    if any(strcmp(par.requests,'itd'))
        itd = reshape(features.itd,n_fb_channel,n_frames_file).';
    end
    if any(strcmp(par.requests,'ic'))
        ic = reshape(features.ic,n_fb_channel,n_frames_file).';
    end
    data = [ild itd ic];
    f_ind = (j-1)*n_frames_file+1:j*n_frames_file;
    feature_data(f_ind,:) = data;

    % Reshape targets to table structure
    t_ind = (j-1)*par.nAngles+1:j*par.nAngles;
    target_data(t_ind,:) = targets;

    % Create reference list
    [~,name,~] = fileparts(feature_filelist{j});
    name_metadata = strsplit(name,'_');
    % Ugly WFS workaround
    if length(name_metadata)<8
        cond_id = 14;
        c_id(f_ind) = cond_id;
        pos = name_metadata{4};
    else
        cond = [name_metadata{2} '_' name_metadata{4}];
        cond_id = strfind(sfs_method,cond);
        c_id(f_ind) = find(not(cellfun('isempty',cond_id)))-1;
        pos = name_metadata{5};
    end
    pos = regexpi(pos,'\d+','match');
    p_id(f_ind) = str2double(pos{1})-1;

    disp(['Reshaped file ' num2str(j)])
end

% Create lookup table for ID with python-style indexing 
p_id = stretch_vector(p_id,n_subjects);
c_id = stretch_vector(c_id,n_subjects);
ref_list_ID_table = table(global_id,p_id.',c_id.',s_id,...
    'VariableNames',{'global_id','pos_id','cond_id','subject_id'});

% Create lookup table for position with python-style indexing
pos_idx = (0:length(x)-1).';
pos_table = table(pos_idx,x,y,'VariableNames',{'pos_id','x','y'});

% creat lookup table for condition (method_parameter) with python-style indexing
cond_idx = (0:length(sfs_method)-1).';
cond_table = table(cond_idx,sfs_method,'VariableNames',{'cond_id','sfs_method'});

% Creat lookup table for setup with python-style indexing
setup_idx = (0:length(setup)-1).';
setup_table = table(setup_idx,setup,'VariableNames',{'setup_id','setup'});

% Create data tables for features and targets
var_t = strcat('subject_', strsplit(num2str(1:n_subjects)));
target_table = array2table(target_data,'VariableNames', var_t);
var_f = insert_num2str({'ILD_','ITD_','IC_'},par.cfHz,'Hz',0);
feature_table = array2table(feature_data, 'VariableNames', var_f);

%% Save to files

% Write feature data
disp('Writing feature data...');
writetable(feature_table,fullfile(export_dir,'feature_data.csv'));
disp('Done.');

% Write target data
disp('Writing target data...');
writetable(target_table,fullfile(export_dir,'target_data.csv'));
disp('Done.');

% Write id reference table (global_id)
disp('Writing id reference table...');
writetable(ref_list_ID_table,fullfile(export_dir,'ID_reference_table.csv'));
disp('Done.');

% Write position table (pos_id)
disp('Writing position table...');
writetable(pos_table,fullfile(export_dir,'position_table.csv'));
disp('Done.');

% Write condition table (cond_id)
disp('Writing condition table...');
writetable(cond_table,fullfile(export_dir,'condition_table.csv'));
disp('Done.');

% Write setup table (setup_id)
%disp('Writing setup table...');
%writetable(setup_table,'setup_table.csv');
%disp('Done.');

% Write feature structure info to file
size_table = struct2table(par);
writetable(size_table,fullfile(export_dir,'feature_par.csv'));
disp('Everything done.');

% =========================================================================

function [x_s] = stretch_vector(x,n)
%STRETCH_VECTOR stretches a given row vector of length N by factor n, so
% that the resulting length equals N*n.
% For example: x = [1 2 3] n = 2 --> x_s = [1 1 2 2 3 3] 
%
%   Input parameters:
%       x   - row vector [1xN]
%       n   - integer factor
%
%   Output parameters:
%       x_s - stretched row vector [1xN*n]

s = repmat(x,n,1);
x_s = s(1:end);
end