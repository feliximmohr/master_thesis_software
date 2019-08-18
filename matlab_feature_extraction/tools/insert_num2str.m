function [strcell_out] = insert_num2str(str1,mat,str2,N)
%INSERT_NUM2STR inserts each number in mat between strings str1 and str2.
%   Numbers are rounded to N digits. In case str1 is a cell array execute
%   for str in each cell. Returns cell array of strings.

if nargin<3; str2=''; end
if nargin<4; N = 1; end

% Check if str is cell array
str1_iscell = iscell(str1);
if str1_iscell
    n_cells = length(str1);
else
    str1 = {str1};
    n_cells = 1;
end
% Round mat to N digits
n_num = length(mat);
mat = round(mat,N);
% Insert number between str1 and str2 for each number and each cell in str1
strcell_out = cell(1,n_cells*n_num);
for i=1:n_cells
    for j=1:n_num
        strcell_out{1,(i-1)*n_num+j} = [str1{i},num2str(mat(j)),str2];
    end
end
end