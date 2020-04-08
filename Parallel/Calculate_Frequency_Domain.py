from collections import namedtuple
from typing import List
from typing import Tuple
from astropy.timeseries import LombScargle
import numpy as np


# Lomb Scargle Tools 
# from Library.utils import _get_features_from_psd
# from Library.utils import _get_freq_psd_from_nn_intervals
# from Library.utils import _create_timestamp_list

# Named Tuple for different frequency bands
UlfBand = namedtuple("Ulf_band", ["low", "high"])
VlfBand = namedtuple("Vlf_band", ["low", "high"])
LfBand = namedtuple("Lf_band", ["low", "high"])
HfBand = namedtuple("Hf_band", ["low", "high"])

# Frequency Methods name
WELCH_METHOD = "welch"
LOMB_METHOD = "lomb"

def _create_timestamp_list(nn_intervals: List[float]) -> List[float]:

    # Convert in seconds
    nni_tmstp = np.cumsum(nn_intervals) / 1000

    # Force to start at 0
    return nni_tmstp - nni_tmstp[0]

def _get_freq_psd_from_nn_intervals(nn_intervals: List[float], method: str = LOMB_METHOD,
                                    sampling_frequency: int = 4,
                                    interpolation_method: str = "linear",
                                    ulf_band: namedtuple = UlfBand(0, 0.00333),
                                    vlf_band: namedtuple = VlfBand(0.00334, 0.04),
                                    hf_band: namedtuple = HfBand(0.15, 0.40)) -> Tuple:

    timestamp_list = _create_timestamp_list(nn_intervals)



    if method == LOMB_METHOD:
        freq, psd = LombScargle(timestamp_list, nn_intervals,
                                normalization='psd').autopower(minimum_frequency=ulf_band[0],
                                                               # THIS WHERE I CHANGED VLF_BAND TO ULF_BAND
                                                               maximum_frequency=hf_band[1])
    else:
        raise ValueError("Not a valid method. Choose between 'lomb' and 'welch'")

    return freq, psd


def _get_features_from_psd(freq: List[float], psd: List[float], 
                           ulf_band: namedtuple = UlfBand(0, 0.00333),
                           vlf_band: namedtuple = VlfBand(0.00333, 0.04),
                           lf_band: namedtuple = LfBand(0.04, 0.15),
                           hf_band: namedtuple = HfBand(0.15, 0.40)) -> dict:

    # Calcul of indices between desired frequency bands
    ulf_indexes = np.logical_and(freq >= ulf_band[0], freq < ulf_band[1])
    vlf_indexes = np.logical_and(freq >= vlf_band[0], freq < vlf_band[1])
    lf_indexes = np.logical_and(freq >= lf_band[0], freq < lf_band[1])
    hf_indexes = np.logical_and(freq >= hf_band[0], freq < hf_band[1])

    # Integrate using the composite trapezoidal rule
    lf = np.trapz(y=psd[lf_indexes], x=freq[lf_indexes])
    hf = np.trapz(y=psd[hf_indexes], x=freq[hf_indexes])

    # total power & vlf : Feature often used for  "long term recordings" analysis
    ulf = np.trapz(y=psd[ulf_indexes], x=freq[ulf_indexes])
    vlf = np.trapz(y=psd[vlf_indexes], x=freq[vlf_indexes])
    total_power = ulf + vlf + lf + hf

    lf_hf_ratio = lf / hf
    lfnu = (lf / (lf + hf)) * 100
    hfnu = (hf / (lf + hf)) * 100

    freqency_domain_features = {
        'lf': lf,
        'hf': hf,
        'lf_hf_ratio': lf_hf_ratio,
        'lfnu': lfnu,
        'hfnu': hfnu,
        'total_power': total_power,
        'vlf': vlf,
        'ulf' : ulf
    }

    return freqency_domain_features

def Calculate_Lomb_Scargle(nn_intervals: List[float], method: str = LOMB_METHOD,
                                  sampling_frequency: int = 4, interpolation_method: str = "linear",
                                  ulf_band: namedtuple = UlfBand(0, 0.00333),
                                  vlf_band: namedtuple = VlfBand(0.00334, 0.04),
                                  lf_band: namedtuple = LfBand(0.04, 0.15),
                                  hf_band: namedtuple = HfBand(0.15, 0.40)) -> dict:

    # ----------  Compute frequency & Power spectral density of signal  ---------- #
    freq, psd = _get_freq_psd_from_nn_intervals(nn_intervals=nn_intervals, method=method,
                                                sampling_frequency=sampling_frequency,
                                                interpolation_method=interpolation_method,
                                                ulf_band=ulf_band,
                                                vlf_band=vlf_band, hf_band=hf_band)

    # ---------- Features calculation ---------- #
    freqency_domain_features = _get_features_from_psd(freq=freq, psd=psd,
                                                      ulf_band=ulf_band,
                                                      vlf_band=vlf_band,
                                                      lf_band=lf_band,
                                                      hf_band=hf_band)

    return freqency_domain_features