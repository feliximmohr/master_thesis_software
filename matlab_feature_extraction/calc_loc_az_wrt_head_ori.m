function calc_loc_az_wrt_head_ori(stats_dir,export_dir)
%CALC_LOC_AZ_WRT_HEAD_ORI calculates the localization azimuth with respect 
% to head orientation for all conditions and write results to csv file.
%   #TODO: extended documentation
%
%   Usage: calc_loc_az_wrt_head_ori(stats_dir,export_dir)
%
%   Input parameters:
%       stats_dir   - path to data set directory
%       export_dir  - path to directory to save the computation outcome
% 

%% Get filenames
filenames = dir([stats_dir, '*_corrected_azimuth.txt']);
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

% Compute for each file corresponding to one condition (sfs method + setup)
for i=1:size(filenames)
    % Import data
    data = readmatrix([stats_dir, filenames(i).name]);
    data(1,:) = [];
    % Localization azimuth as mxn matrix; n subjects for m positions
    data = data(:,6:25);
    
    % Compute for each position
    for j=1:size(data,1)
        loc_az = data(j,:);
        % Calculate azimuth
        head_or = (0:359).';
        loc_az = loc_az + (loc_az<0)*360;
        az_wrt_head = loc_az - head_or;
        az_wrt_head = wrapTo180(az_wrt_head);
        % Save to csv file
        pos_idx = int2str(j);
        if length(pos_idx)<2; pos_idx=['0',pos_idx]; end
        filename_out = [filenames_out{i},'_pos',pos_idx,'_az_wrt_head.csv'];
        writematrix(az_wrt_head,filename_out);
    end
end
end