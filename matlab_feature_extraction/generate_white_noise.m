% Generate normally distributed white noise normalized to 1

fs = 44100;
t = 1;
s = rng(1234);
wn = randn(fs*t, 1);
wn = wn/max(abs(wn));
save('../generated/wn.mat', 'wn')