"""Data preprocessing for the new chip 
    23/03/2023, sampling frequency = 500Hz, lead_order = ["I II V1 V2 V3 V4 V5 V6"]
    need to calculate the augmented leads"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__all__ = ["read_ECGdata", "downsampling", "ECG_standardization", "ECG_standardization_singlelead", "ECG_plot"]

def read_ECGdata(FILE_PATH, 
                 data_column_number, 
                 need_augmentation=False, 
                 lead_arrangement=False,
                 voltage_standardization=True,
                 skiprow=3, 
                 deepcopy=True):

    all_data = pd.read_csv(FILE_PATH, skiprows=skiprow)
    
    if deepcopy == True:
        raw_data = all_data.copy()
        raw_data = all_data.to_numpy()
        raw_data = raw_data[:, :data_column_number]
    else:
        raw_data = all_data.to_numpy()
        raw_data = raw_data[:, :data_column_number]

    if need_augmentation:
        # aVL = Lead I - (Lead II / 2)
        # aVF = Lead II - (Lead I / 2)
        # aVR = -(Lead I + Lead II) / 2
        #Lead III = Lead aVF - Lead aVL
        ecg = raw_data
        
        avR = np.negative((ecg[:, 0] + ecg[:, 1]) / 2)
        ecg = np.hstack((ecg, avR.reshape(-1, 1)))
        
        avL = ecg[:, 0] - (ecg[:, 1] / 2)
        ecg = np.hstack((ecg, avL.reshape(-1, 1)))

        avF = ecg[:, 1] - (ecg[:, 0] / 2)
        ecg = np.hstack((ecg, avF.reshape(-1, 1)))

        l3 = np.subtract(avF, avL)
        ecg = np.hstack((ecg, l3.reshape(-1, 1)))
        
        raw_data = ecg  #shape (m, 12)
    
    if lead_arrangement:
        ecg = raw_data
        
        # ["I II V1 V2 V3 V4 V5 V6 avR avL avF III"]
        #lead_index = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        permutation = [0, 1, 11, 8, 9, 10, 2, 3, 4, 5, 6, 7]
        #permutation = [0, 1, 6, 7, 8, 9, 10, 11, 3, 4, 5, 2]
        idx = np.empty_like(permutation)
        idx[permutation] = np.arange(len(permutation))
        ecg = ecg[:, idx]

        raw_data = ecg
        #print(np.shape(ecg))
    
    # voltage standardization
    if voltage_standardization:
        #calculating real voltage of data
        vref = 2.4;  # Unit(V)
        w = vref / (np.power(2, 23) - 1);
        gain = 6;
        raw_data = raw_data * w / gain * 1000;  # get real voltage of the data in mV
    
    return raw_data


def downsampling(ecg, acc=None):
    """Down-sampling"""
    # Cut half of the raw data from 1000 to 500Hz
    data_length = len(ecg[:, 0]) // 2
    #print(data_length)

    new_ecg = np.empty(shape=[0, data_length])
    new_acc = np.empty(shape=[0, data_length])

    if acc:
        for i in range(3):
            temp = acc[:, i]
            temp = np.transpose(temp)
            temp = temp[1::2]
            new_acc = np.vstack([new_acc, temp])

    for i in range(12):
        temp = ecg[:, i]
        temp = np.transpose(temp)
        temp = temp[1::2]

        # print(len(temp))
        new_ecg = np.vstack([new_ecg, temp])

    return new_ecg, new_acc


def ECG_standardization(data, method="zscore", channels=12, start=None, end=None):
    """Standardization of ECG data"""

    if start is None:
        start = 0
    if end is None:
        end = data.shape[0]

    data = np.transpose(data[start:end])

    if method == "zscore":
        std = np.std(data, axis=1)
        mean = np.mean(data, axis=1)
        ecg_std = std.reshape((channels, 1))
        ecg_mean = mean.reshape((channels, 1))
        np.seterr(invalid='ignore')
        z_norm_ecg = (data - ecg_mean) / ecg_std
        norm_ecg = np.transpose(z_norm_ecg)

    elif method == "minmax":
        data_min = np.min(data, axis=1)
        data_max = np.max(data, axis=1)
        data_min = data_min.reshape((channels, 1))
        data_max = data_max.reshape((channels, 1))

        data_norm = (data - data_min) / (data_max - data_min)
        norm_ecg = np.transpose(data_norm)

    elif method == "discrete":
        ecg_min = np.min(data, axis=1)
        ecg_max = np.max(data, axis=1)
        ecg_min = ecg_min.reshape((channels, 1))
        ecg_max = ecg_max.reshape((channels, 1))
        np.seterr(invalid='ignore')
        norm_ecg = np.transpose(data - ecg_min)

    else:
        print("Please select a valid method for ECG standardization")
        norm_ecg = np.empty(shape=np.shape(data))

    return norm_ecg

def ECG_standardization_singlelead(data, method="zscore", start=None, end=None):
    """Standardization of single-lead ECG data"""

    if start is None:
        start = 0
    if end is None:
        end = data.shape[0]


    if method == "zscore":
        std = np.std(data)
        mean = np.mean(data)
        # ecg_std = std.reshape((-1, 1))
        # ecg_mean = mean.reshape((-1, 1))
        np.seterr(invalid='ignore')
        z_norm_ecg = (data - mean) / std
        norm_ecg = np.transpose(z_norm_ecg)

    elif method == "minmax":
        data_min = np.min(data)
        data_max = np.max(data)

        data_norm = (data - data_min) / (data_max - data_min)
        norm_ecg = np.transpose(data_norm)

    elif method == "discrete":
        ecg_min = np.min(data)
        np.seterr(invalid='ignore')
        norm_ecg = np.transpose(data - ecg_min)

    else:
        print("Please select a valid method for ECG standardization")
        norm_ecg = np.empty(shape=np.shape(data))

    return norm_ecg


def ECG_plot(data, single_lead=False, lead=0, start=None, end=None, title=None):
    """Plot ECG data"""
    if start is None:
        start = 0
    if end is None:
        end = data.shape[0]

    time = np.arange(start, end) / 500
    
    if single_lead:
        plt.figure(figsize=(15, 8))
        plt.plot(time, data[start:end])
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (mV)")
        if title:
            plt.title(title)
        plt.show()
    else:
        plt.figure(figsize=(15, 8))
        plt.plot(time, data[start:end, lead])
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (mV)")
        if title:
            plt.title(title)
        
        plt.show()
    

#test case
# ECG_data = read_ECGdata("C:/Users/zzhaobz/Documents/Python_Code/Projects/2022/ECG/ecg_signal_pps_2022/data_preprocessed/2023/23032023/WAVE(2023.3.23-15.20.28).csv", \
#                     data_column_number=8, need_augmentation=True, lead_arrangement=True, skiprow=3)


# norm_ecg = ECG_standardization(ECG_data, channels=12, method="zscore", start=2000, end=4000)
# ECG_plot(norm_ecg, single_lead=True, start=0, end=2000, title="ECG Lead I")