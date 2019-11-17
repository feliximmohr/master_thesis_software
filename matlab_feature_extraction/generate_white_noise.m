% Generate normally distributed white noise normalized to 1 and save to .mat
% file.

fs = 44100;
t = 1;
s = rng(1234);
wn = randn(fs*t, 1);
stimulus = wn/max(abs(wn));
save('../generated/wn.mat', 'stimulus','fs')