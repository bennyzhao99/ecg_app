ECG Analysis App
================

An ECG Analysis App developed by Zibin ZHAO @Hsing Group, HKUST.
This application allows users to read, process, and visualize electrocardiogram (ECG) data.
Users can also apply various filters to the ECG data and save the processed data and plots.

Features:
---------
- Import ECG data in CSV format
- Select ECG leads
- Apply data preprocessing options
- Apply filters to ECG data (e.g., baseline wandering, powerline interference)
- Visualize raw and filtered ECG data
- Save filtered data and plots

Dependencies:
-------------
- numpy
- pandas
- matplotlib
- tkinter
- ecg_filter (custom module)
- data_preprocess (custom module)

Usage:
------
1. Run the script python main.py.
2. Browse and select an ECG data file in CSV format.
3. Choose the desired ECG lead and set data preprocessing options.
4. Set the start and end indices for the ECG data.
5. Select one or multiple filters to apply to the ECG data.
6. Click "Process ECG Data" to process the data.
7. Click "Plot ECG" to visualize the raw and filtered ECG data.
8. Save the filtered ECG data and plots by clicking "Save Filtered Data" and "Save Plot" buttons.

Tips:
---
- If you do not want to reopen your input file, simpliy select the new lead index and click process ECG, and then you are able to visualize the new lead data in the plot.

Contributing:
-------------
Please feel free to report any issues or suggest improvements by creating an issue or submitting a pull request.

License:
--------
This project is licensed under the MIT License.

