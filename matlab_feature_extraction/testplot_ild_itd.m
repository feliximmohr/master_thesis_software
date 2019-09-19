function testplot_ild_itd(cf,data,fs,scaling)
%PLOT_ILD_ITD Summary of this function goes here
%   Detailed explanation goes here
if nargin < 4
    scaling = 1;
end

t = 0:1/fs:(size(data,2)-1)/fs;
M = size(cf,2);

%plot
if scaling
    imagesc(t,1:M, data);
else
    imagesc(data);
end
colormap('jet')
axis xy

end

