% Script to start feature extraction for specified data sets
%TODO:

clear
close all
clc
addpath('tools');

dataset_dir = {'../generated/exp1/'
               '../generated/exp2/'};
export_dir  =  '../generated/';
           
% Define metadata
% Listening positions
x = [0.00; 0.50; 1.00; 0.00; 0.50; 1.00; 1.25;  0.00;  0.50;  1.00]*(-1);
y = [0.75; 0.75; 0.75; 0.00; 0.00; 0.00; 0.00; -0.75; -0.75; -0.75];

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
setup = {'circular_nls0056_dvs3.00'};          

%% Processing
T_all=table();
% Do for each data set (exp1/exp2/...)
for i=1:size(dataset_dir,1)
% Get filenames
features_dir = [dataset_dir{i},'features/'];
targets_dir  = [dataset_dir{i},'targets/'];
[features_files,num] = get_filelist(features_dir);
[targets_files,~] = get_filelist(targets_dir);

% Load each file
for j=1:num
% Load data
features = load(fullfile(features_dir,features_files{j}));
targets = load(fullfile(targets_dir,targets_files{j}));

% Assign data to condition (sfs method and setup)
[be,en] = regexpi(features_files{j},'_[\w-]+_L\d+_\w\d+_');
condition = regexprep(features_files{j}(be+1:en-1),'_L\d+','');
method_idx = find(strcmp(sfs_method, condition));

% Assign data to position
[be,en] = regexpi(features_files{j},'pos\d+');
pos_idx = str2double(features_files{j}(be+3:en));

% Get number of resulting entries per file (per 1 position/condition)
num_cfHz = size(features.cfHz,2);
num_fsamples = size(features.ild,2);
num_tsamples = size(targets,2);
num_entries = 360 * num_fsamples * num_tsamples;

[x_t,y_t] = deal(zeros(num_entries,1));
x_t(:) = x(pos_idx);
y_t(:) = y(pos_idx);

[sfs_method_t{1:num_entries,1}] = deal(sfs_method{method_idx});
[setup_t{1:num_entries,1}] = deal(setup{1});

%test = zeros(num_entries,4);
%cfHz = repmat(features.cfHz,num_fsamples,1);
%cfHz = cfHz(:);

variables_data = insert_num2str({'ILD_','ITD_','IC_'},features.cfHz,'Hz',0);
variables_meta = {'x','y','SFS_Method','Setup'};
variables_all = [variables_meta,variables_data];

ild_t = permute(features.ild,[2 1 3]);
ild_t = vertcat_dim3(ild_t);
ild_t = repmat(ild_t,num_tsamples,1);
itd_t = permute(features.itd,[2 1 3]);
itd_t = vertcat_dim3(itd_t);
itd_t = repmat(itd_t,num_tsamples,1);
ic_t = permute(features.ic,[2 1 3]);
ic_t = vertcat_dim3(ic_t);
ic_t = repmat(ic_t,num_tsamples,1);

targets_t = zeros(num_entries,1);
for q=1:num_tsamples
    b = q*(num_fsamples*360);
    a = (q-1)*(num_fsamples*360)+1;
    t = repmat(targets(:,q),1,num_fsamples)';
    targets_t(a:b,1) = t(:);
end

T1 = array2table([ild_t,itd_t,ic_t,targets_t],'VariableNames',[variables_data,'Localization_Azimuth']);

T2 = table(x_t,y_t,sfs_method_t,setup_t, 'VariableNames', variables_meta);

T=[T2,T1];
T_all = [T_all;T];
%HERE: cfHz as feature
% variables = {'x','y','SFS Method','Setup','cfHz', 'ILD', 'ITD', 'IC','localization azimuth'};
% for k=1:num_entries
%     T_n = table(x,y,sfs_method,setup,cfHz,features.ild(:,:,i).',features.itd(:,:,i).',features.ic(:,:,i).',targets.loc_az, 'VariableNames', variables);
%     T = [T;T_n];
% end
writetable(T_all,'data_set2.csv')
end

end

% Write table to file
writetable(T_all,'data_set.csv')
