function powerDb = combineRxPower(spectrum)
%COMBINERXPOWER Noncoherent RX power combination.
%
%   powerDb = awr2944.combineRxPower(spectrum)
%
%   spectrum : complex double [rangeBins, rx, doppler/chirp, frame]
%
%   Returns powerDb : double [rangeBins, 1, doppler/chirp, frame]
%       Sum of |X|^2 across RX channels, in dB.

    rxPower = sum(abs(spectrum).^2, 2);   % sum over rx (dim 2)
    powerDb = 10 * log10(max(rxPower, eps));
end
