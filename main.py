"""An ECG app developed by Zibin ZHAO @Hsing Group, HKUST, starting 04/04/2023"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ecg_filter import *
from data_preprocess import *

canvas = None

def reset():
    global ECG_data, filtered_ecg, canvas, selected_lead, selected_filters

    ECG_data = None
    filtered_ecg = None
    selected_lead.set("Lead I")
    selected_filters = []

    if canvas:
        canvas.get_tk_widget().pack_forget()
        canvas = None

    process_button.config(state=tk.DISABLED)
    plot_button.config(state=tk.DISABLED)

    start_entry.delete(0, tk.END)
    end_entry.delete(0, tk.END)
    filter_menu.set("None")
    selected_filters_label.config(text="")


def process_ECG():
    global ECG_data, filtered_ecg, canvas, start_entry, end_entry, selected_filters, lead_index, selected_range

    start_index = int(start_entry.get()) if start_entry.get() else None
    end_index = int(end_entry.get()) if end_entry.get() else None
    selected_range = slice(start_index, end_index)
    lead_index = lead_options.index(selected_lead.get())
    filtered_ecg = ECG_standardization_singlelead(ECG_data[selected_range, lead_index], method="zscore")

    print(selected_filters)
    for filt in selected_filters:
        temp_filtered_ecg = filtered_ecg.copy()
        if filt == "Baseline Wander":
            temp_filtered_ecg = BW_removal(filtered_ecg)
        elif filt == "HPF (fc=0.5)":
            temp_filtered_ecg = HPF_removal(filtered_ecg)
        elif filt == "Powerline Interference":
            temp_filtered_ecg = PLI_removal(filtered_ecg)
        elif filt == "Moving Average (8-points)":
            temp_filtered_ecg = MA_removal(filtered_ecg)
        filtered_ecg = temp_filtered_ecg

    plot_button.config(state=tk.NORMAL)


def plot_ecg():
    global filtered_ecg, ECG_data, selected_range
    
    raw_ecg = ECG_data[selected_range, lead_index]
    fig = plt.Figure(figsize=(12, 6))

    # Raw ECG subplot
    ax1 = fig.add_subplot(211)
    ax1.plot(raw_ecg)
    ax1.set(xlabel="Time (s)", ylabel="Voltage (mV)")
    ax1.set_title("Raw ECG")

    # Filtered ECG subplot
    ax2 = fig.add_subplot(212)
    ax2.plot(filtered_ecg)
    ax2.set(xlabel="Time (s)", ylabel="Voltage (mV)")
    ax2.set_title("Filtered ECG")

    # Create a new window for the plot
    plot_window = tk.Toplevel(window)
    plot_window.geometry("800x600")
    plot_window.title("ECG Plot")

    global canvas
    # if canvas:
    #     canvas.get_tk_widget().pack_forget()
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
    
    # Add "Save Plot" button to the new window
    save_plot_button = ttk.Button(plot_window, text="Save Plot", command=save_plot)
    save_plot_button.pack(side=tk.BOTTOM)



def browse_file():
    global ECG_data
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not filepath:
        return
    ECG_data = read_ECGdata(
        filepath,
        data_column_number=8,       # set this with different chips
        need_augmentation=need_augmentation_var.get(),
        lead_arrangement=lead_arrangement_var.get(),
        voltage_standardization=voltage_standardization_var.get(),
        skiprow=3
    )
    process_button.config(state=tk.NORMAL)


def save_filtered_data():
    global filtered_ecg
    if filtered_ecg is None:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")])
    if file_path.endswith(".csv"):
        np.savetxt(file_path, filtered_ecg, delimiter=",")
    elif file_path.endswith(".xlsx"):
        df = pd.DataFrame(filtered_ecg)
        df.to_excel(file_path, index=False)


def save_plot():
    global filtered_ecg
    if filtered_ecg is None:
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("SVG Files", "*.svg"), ("PDF Files", "*.pdf")]
    )
    if file_path:
        fig, ax = plt.subplots()
        ax.plot(filtered_ecg[:, 0])
        fig.savefig(file_path)
        plt.close(fig)

def add_filter(*args):
    selected_filter = filter_menu.get()
    if selected_filter != "None" and selected_filter not in selected_filters:
        selected_filters.append(selected_filter)
        selected_filters_label.config(text=", ".join(selected_filters))


# Create main window
window = tk.Tk()
window.geometry("650x250")
window.title("ECG Analysis")

style = ttk.Style()
style.configure('TButton', font=('Arial', 10))
style.configure('TLabel', font=('Arial', 10))
style.configure('TCheckbutton', font=('Arial', 10))
style.configure('TCombobox', font=('Arial', 10))

control_frame = tk.Frame(window)
control_frame.pack(fill=tk.BOTH, expand=True)

for i in range(4):
    control_frame.columnconfigure(i, weight=1)



# Create buttons for browsing, processing, resetting and saving ECG data
browse_button = ttk.Button(control_frame, text="Browse ECG File", command=browse_file)
browse_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

process_button = ttk.Button(control_frame, text="Process ECG Data", state=tk.DISABLED, command=process_ECG)
process_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

plot_button = ttk.Button(control_frame, text="Plot ECG", state=tk.DISABLED, command=plot_ecg)
plot_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

reset_button = ttk.Button(control_frame, text="Reset", command=reset)
reset_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

save_filtered_button = ttk.Button(control_frame, text="Save Filtered Data", command=save_filtered_data)
save_filtered_button.grid(row=4, column=0, padx=5, pady=5)


# Create checkboxes and dropdown menu for selecting ECG lead and data processing options
need_augmentation_var = tk.BooleanVar(value=True)
need_augmentation_cb = ttk.Checkbutton(control_frame, text="Need Augmentation", variable=need_augmentation_var)
need_augmentation_cb.grid(row=1, column=0, padx=5, pady=5)

lead_arrangement_var = tk.BooleanVar(value=True)
lead_arrangement_cb = ttk.Checkbutton(control_frame, text="Lead Arrangement", variable=lead_arrangement_var)
lead_arrangement_cb.grid(row=1, column=1, padx=5, pady=5)

voltage_standardization_var = tk.BooleanVar(value=True)
voltage_standardization_cb = ttk.Checkbutton(control_frame, text="Voltage Standardization", variable=voltage_standardization_var)
voltage_standardization_cb.grid(row=1, column=2, padx=5, pady=5)

# Create and configure the lead menu
lead_options = ["Lead I", "Lead II", "Lead III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
selected_lead = tk.StringVar(control_frame)
selected_lead.set("Lead I")
lead_menu = ttk.OptionMenu(control_frame, selected_lead, *lead_options)
lead_menu.grid(row=1, column=3, pady=(10, 0))

start_entry_label = ttk.Label(control_frame, text="Start Index:")
start_entry_label.grid(row=2, column=0)
start_entry = ttk.Entry(control_frame)
start_entry.grid(row=2, column=1)

end_entry_label = ttk.Label(control_frame, text="End Index:")
end_entry_label.grid(row=2, column=2)
end_entry = ttk.Entry(control_frame)
end_entry.grid(row=2, column=3)


# NOTE: name must match the filtering function name!!!!!!
filter_options = ["None", "Baseline Wander", "Powerline Interference", "Moving Average (8-points)", "HPF (fc=0.5)"]     
selected_filters = []

# Create and configure the filter menu
filter_label = ttk.Label(control_frame, text="Select Filter:")
filter_label.grid(row=3, column=0, pady=(10, 0), sticky=tk.E)
filter_menu = tk.StringVar(control_frame)
filter_menu.set("None")
filter_option_menu = ttk.OptionMenu(control_frame, filter_menu, *filter_options, command=add_filter)
filter_option_menu.grid(row=3, column=1, pady=(10, 0), sticky=(tk.W, tk.E))

selected_filters_label = ttk.Label(control_frame, text="")
selected_filters_label.grid(row=3, column=2, columnspan=2, pady=(10, 0), sticky=tk.W)



# Add widgets to the control_frame
need_augmentation_cb.grid(row=1, column=0, padx=5, pady=5)
lead_arrangement_cb.grid(row=1, column=1, padx=5, pady=5)
voltage_standardization_cb.grid(row=1, column=2, padx=5, pady=5)
lead_menu.grid(row=1, column=3, padx=5, pady=5)
start_entry_label.grid(row=2, column=0, padx=5, pady=5)
start_entry.grid(row=2, column=1, padx=5, pady=5)
end_entry_label.grid(row=2, column=2, padx=5, pady=5)
end_entry.grid(row=2, column=3, padx=5, pady=5)
filter_label.grid(row=3, column=0, padx=5, pady=5)
filter_option_menu.grid(row=3, column=1, padx=5, pady=5)
selected_filters_label.grid(row=3, column=2, columnspan=2, padx=5, pady=5)

# Start the main event loop
window.mainloop()
