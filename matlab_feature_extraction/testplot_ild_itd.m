function testplot_ild_itd(cf,data)
%PLOT_ILD_ITD Summary of this function goes here
%   Detailed explanation goes here
t = 0:1/fs:(size(data,2)-1)/fs;
M = size(cf,2);

%plot
imagesc(t,1:M, data);
colomap('jet')
axis xy

end

