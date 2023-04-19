"""Filtering of ECG signal for the new chip, transferred from previous MATLAB script."""

import numpy as np
from scipy.signal import iirnotch, filtfilt
import matplotlib.pyplot as plt
import pywt
from data_preprocess import *
from scipy import signal


__all__ = ["BW_removal", "PLI_removal", "MA_removal", "calculate_snr", "HPF_removal"]



def BW_removal(ecg):
    # Wavelet implementation for sampling frequency of 500
    coeffs = pywt.wavedec(ecg, 'db9', level=10)

    # Create a new list of coefficients with zeros for the ones not being used
    new_coeffs = [np.zeros_like(coeffs[i]) if i < 1 or i > 9 else coeffs[i] for i in range(11)]

    # Reconstruct signal from cd3 to cd9 % Range from 0.5-125Hz
    bw_ecg = pywt.waverec(new_coeffs, 'db9')

    return bw_ecg

def HPF_removal(ecg):
    # Define filter specifications
    fc = 0.5  # Cut-off frequency
    fs = 500  # Sampling frequency
    order = 4  # Filter order

    # Calculate filter coefficients
    b, a = signal.butter(order, fc / (fs/2), 'high')
    output = signal.filtfilt(b, a, ecg)
    return output

def PLI_removal(ecg):
    fs = 500
    w = 50  # notch frequency 50Hz with sampling frequency of 500
    bw = w  # bandwidth
    Q = 50  # quality factor
    num, den = iirnotch(w / (fs / 2), Q)  # notch filter implementation
    pli_ecg = filtfilt(num, den, ecg)
    return pli_ecg



def MA_removal(ecg):
    # 8-points
    MA_ecg = np.convolve(ecg, np.ones(8)/8, mode='same')
    return MA_ecg



def calculate_snr(signal, noise):
    # Calculate the power of the signal and noise
    signal_power = np.mean(np.square(signal))
    noise_power = np.mean(np.square(noise))

    # Calculate the SNR in decibels
    snr_db = 10 * np.log10(signal_power / noise_power)

    return snr_db




# Test
# ECG_data = read_ECGdata("C:/Users/zzhaobz/Documents/Python_Code/Projects/2022/ECG/ecg_signal_pps_2022/data_preprocessed/2023/23032023/WAVE(2023.3.23-15.20.28).csv", \
#                          data_column_number=8, need_augmentation=True, lead_arrangement=True, skiprow=3)


# norm_ecg = ECG_standardization(ECG_data, channels=12, method="zscore", start=2000, end=4000)
# print(norm_ecg[:, 0].shape)

# # coeffs = pywt.wavedec(norm_ecg[:, 0], 'db9', level=10)
# # print(len(coeffs))

# bw_removed_ecg = BW_removal(norm_ecg[:, 0])
# pli_removed_ecg = pli_removal(bw_removed_ecg)


# ECG_plot(pli_removed_ecg, single_lead=True, title="Bandwidth removed ECG signal")