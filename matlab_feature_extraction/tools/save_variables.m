function save_variables(filename,var_names,variables)
%SAVE_VARIABLES saves variables under their respective names in a .mat file.
% This function prevents the MATLAB save function to fail an a parfor loop.
s = cell2struct(variables(1:length(var_names)),var_names,2);
save(filename,'-struct','s')
end