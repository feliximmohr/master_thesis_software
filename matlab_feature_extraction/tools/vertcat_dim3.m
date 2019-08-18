function [B] = vertcat_dim3(A)
%VERTCAT_DIM3 concatenates the 3rd dimension of an array along the first
% dimension.

if length(size(A))~=3
    error('Error. \nInput must be 3-dimensional.')
end

B = permute(A,[1 3 2]);
B = reshape(B,[],size(A,2),1);
end

