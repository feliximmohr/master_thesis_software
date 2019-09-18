function [filelist, num_files] = get_filelist(directory)
%GET_FILELIST lists all files in a directory and returns a cell array of
% strings containing the filenames.

% Get file and folder attributes
files = dir(directory);
% Ignore folders
file_flags = ~[files.isdir];
files = files(file_flags);
% Write filenames in cell array
num_files = length(files);
[filelist{1:num_files}] = deal(files.name);
% Sort filelist
filelist = sortrows(filelist);
end

