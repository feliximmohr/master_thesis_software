% Calculate localization azimuth with respect to head orientation for all
% conditions and write results to csv file.
%

% Specify output type ('file_per_cond_pos', 'file_per_cond')
output_type = 'file_per_cond_pos';

%% Set paths
dataset_name = 'exp1';
stats_dir = ['../data_set/',dataset_name,'/analysis/stats/'];
filenames = dir([stats_dir, '*_corrected_azimuth.txt']);
export_dir = ['../generated/',dataset_name,'/targets/'];
% Create dir if not existing
if ~exist(export_dir,'dir'); mkdir(export_dir); end


% Reformat filenames
filenames_out = {filenames(:).name}.';
for i=1:size(filenames_out)
    [~,filenames_out{i},~] = fileparts(filenames_out{i});
    filenames_out{i} = extractBefore(filenames_out{i},'_corr');
    filenames_out{i} = [export_dir, filenames_out{i}];
end

%% Computation
for i=1:size(filenames)
    % Import data
    data = readmatrix([stats_dir, filenames(i).name]);
    data(1,:) = [];
    loc_az = data(:,3);
    % Calculate azimuth
    head_or = 0:359;
    loc_az = loc_az + (loc_az<0)*360;
    az_wrt_head = loc_az - head_or;
    az_wrt_head = wrapTo180(az_wrt_head);
    
    % Save to csv file
    if strcmp(output_type,'file_per_cond_pos')
        % If specified, one file per position/condition
        for j=1:10            
        writematrix(az_wrt_head(j,:).',[filenames_out{i},'_pos',int2str(j),'_az_wrt_head.csv'])
        end
    else
        writematrix(az_wrt_head.',[filenames_out{i},'_az_wrt_head.csv']);
    end
end