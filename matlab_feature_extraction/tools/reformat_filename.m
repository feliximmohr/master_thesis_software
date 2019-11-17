function [namelist_out] = reformat_filename(namelist,dataset_name,file_content)
%REFORMAT_FILENAME reformats the filenames into a special representation.
%   Takes list of strings (cell array) as input. May be too intricate.
sep = '_';

namelist_out = cell(1,length(namelist));

% listening positions
x = [0.00; 0.50; 1.00; 0.00; 0.50; 1.00; 1.25;  0.00;  0.50;  1.00]*(-1);
y = [0.75; 0.75; 0.75; 0.00; 0.00; 0.00; 0.00; -0.75; -0.75; -0.75];
pos = [x,y];

% Search for sfs method in list
sfs_method_str = regexpi(namelist,...
    '_(lwfs-[a-zA-Z]+|wfs|nfchoa)(_|\.)','match');
% Search for reproduction setup in list
setup_str = regexpi(namelist,'_\w+_nls\d+_dls(\d|\.)+','match'); 
% Search for sfs parameters in list
sfs_parameters_str = regexpi(namelist,...
    '(win-[-\w]*_ord-\d+)|_((M|R)\d+_[-\w]*)|(vss_[.\w]*)\.','match');
% Search for listener position in list
listener_pos_str = regexpi(namelist,'pos[-.xyz\d]*((\d{2,})|(\())','match');

for i=1:length(namelist)%filename = namelist
    % Reformat sfs method to e.g. LWFS-SBL
    if isempty(sfs_method_str{i}) || isempty(sfs_method_str{i}{1})
        sfs_method = 'NFCHOA';
    else
        sfs_method = upper(regexprep(sfs_method_str{i}{1},'_|\.',''));
    end
    % Reformat reproduction setup to e.g. L56
    if isempty(setup_str{i}) || isempty(setup_str{i}{1})
        setup = 'L56';
    else
        setup = regexpi(setup_str{1}{1},'ls\d{2,}','match');
        setup = ['L',int2str(str2double(setup{1}(3:end)))];
    end
    % Reformat sfs parameters to e.g. R003
    % Windowing type/VSS radius
    if isempty(sfs_parameters_str{i}) || isempty(sfs_parameters_str{i}{1})
        warning('No sfs parameters found in filename!');
        sfs_parameters = '';
    else
        if strfind(sfs_parameters_str{i}{1},'max-rE')
            sfs_parameters = 'M';
        elseif strfind(sfs_parameters_str{i}{1},'rect')
            sfs_parameters = 'R';
        elseif strfind(sfs_parameters_str{i}{1},'vss')
            sfs_parameters = regexpi(sfs_parameters_str{i}{1},...
                '\d+\.\d+','match');
            sfs_parameters = str2double(sfs_parameters{1})*100/2;
            sfs_parameters = ['r',int2str(sfs_parameters)];
        end
        % Order
        order = regexpi(sfs_parameters_str{i}{1},'(M\d+)|(ord-\d+)','match');
        order = regexpi(order,'\d+','match');
        if ~isempty(order)
            order = order{1}{1};
            while length(order)<3; order=['0',order]; end
            sfs_parameters = [sfs_parameters,order];
        end
    end
    % Reformat listener position
    if isempty(regexpi(listener_pos_str{i}{1},'pos-\d','match'))
        x_n = str2double(regexpi(listener_pos_str{i}{1},'-*\d+\.\d+','match'));
        y_n = str2double(regexpi(listener_pos_str{i}{2},'-*\d+\.\d+','match'));
        pos_n = [x_n,y_n];
        [~,pos_idx] = ismember(pos_n,pos,'rows');
    else
        pos_idx = regexpi(listener_pos_str{i}{1},'\d+','match');
        pos_idx = str2double(pos_idx{1});
    end
    listener_pos = ['pos',int2str(pos_idx-1)];
    
    % Structure new filename
    namelist_out{i} = [dataset_name,sep,sfs_method,sep,setup,sep,...
        sfs_parameters,sep,listener_pos,sep,file_content];
end

% ensure only single seperators
namelist_out = strrep(namelist_out,'__','_');

end