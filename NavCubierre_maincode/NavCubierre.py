#!/usr/bin/env python3.12

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys, os

# Load star data
def load_star_data(filename="hygdata_v41.csv"):
    star_data = {}
    data = np.loadtxt(filename, dtype=str, delimiter=',', skiprows=1, usecols=(6, 17, 18, 19, 15)) #using coloumn 15 to graph real star colors was an afterthought
    # load in the star name, spectral type, x, y, and z coordinate
    for row in data:
        name = row[0].strip()
        x = float(row[1].strip())
        y = float(row[2].strip())
        z = float(row[3].strip())
        spectral_type = row[4].strip().upper()
        color = color_2_spectraltype(spectral_type)
        star_data[name] = {'x': x, 'y': y, 'z': z, 'spectral_type': spectral_type, 'color': color}
    return star_data

# Find star color from spectral type; used only for visual graphing
def color_2_spectraltype(spectral_type):
    spectral_type = spectral_type.strip().upper()
    if spectral_type.startswith("O"):
        return 'slateblue'
    elif spectral_type.startswith("B"):
        return 'lightskyblue'
    elif spectral_type.startswith("A"):
        return 'white'
    elif spectral_type.startswith("F"):
        return 'yellow'
    elif spectral_type.startswith("G"):
        return 'orange'
    elif spectral_type.startswith("K"):
        return 'red'
    elif spectral_type.startswith("M"):
        return 'darkred'
    else:
        return 'gold'

class NavCubierreGUI(tk.Tk):
    def __init__(self, star_data):
        super().__init__()
        self.title("NavCubierre Navigation System")
        self.geometry("800x600")
        self.origin_star = tk.StringVar()
        self.destination_star = tk.StringVar()
        self.distance = tk.StringVar()
        self.total_time = tk.StringVar()
        self.star_data = star_data
        self.star_names = sorted(list(self.star_data.keys()))
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bg="#650c00")
        self.bg_canvas.pack(fill="both", expand=True)
        self.background_lines()
        self.create_widgets()
        self.lift()
        self.fortran_executable = "./runge_fuel.exe" # fortran executable set here
        self.stop_flag = False
        self.path_line = None

    def background_lines(self): # Used to make the grid pattern in the background
        line_color = "#e67e22"
        spacing = 20
        for i in range(0, 600, spacing):
            self.bg_canvas.create_line(0, i, 1000, i, fill=line_color)
        for i in range(0, 800, spacing):
            self.bg_canvas.create_line(i, 0, i, 1000, fill=line_color)

    def create_widgets(self):
# Input Frame where users can access the combobox:
        input_frame = tk.Frame(self.bg_canvas, bg="#650c00", bd=2, relief="groove")
        star_fields = [ {"label": "Origin Star:", "variable": self.origin_star, "combobox": None, "row": 1},
                        {"label": "Destination Star:", "variable": self.destination_star, "combobox": None, "row": 2}, ]
# here is where the combobox with a search function is implemented:
        def star_field(config):
            label = tk.Label(input_frame, text=config["label"], background="#650c00", foreground="white")
            label.grid(row=config["row"], column=0, padx=5, pady=5, sticky="w")
            combobox = ttk.Combobox(input_frame, textvariable=config["variable"], values=self.star_names, width=25)
            combobox.grid(row=config["row"], column=1, padx=5, pady=5, sticky="ew")
            config["combobox"] = combobox
            def on_combobox_change(event): # Changed combobox to on_combobox_change
                selected_star = combobox.get()
                config["variable"].set(selected_star)
                self.star_selection() # Changed update_selection to star_selection
            combobox.bind("<<ComboboxSelected>>", on_combobox_change)
            def autocomplete(event):
                value = combobox.get()
                new_values = [item for item in self.star_names if value.lower() in item.lower()]
                combobox['values'] = new_values if value else self.star_names
            combobox.bind('<KeyRelease>', autocomplete)
            config["combobox"] = combobox

        for field_config in star_fields:
            star_field(field_config)

# Creates calculate button displayed with the dropdown menus
        self.calculate_button = tk.Button(input_frame, text="Calculate", command=self.calc_selection)
        self.calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result frame that shows users the time and distance calculated
        result_frame = tk.Frame(self.bg_canvas, bg="#650c00", bd=2, relief="groove")
        self.result_frame = result_frame
        tk.Label(result_frame, text="Calculated Distance (pc):", background="#650c00", foreground="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.calc_dist_label = tk.Label(result_frame, textvariable=self.distance, width=20, bg="white")
        self.calc_dist_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(result_frame, text="Estimated Travel Time (years):", background="#650c00", foreground="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.calc_time_label = tk.Label(result_frame, textvariable=self.total_time, width=20, bg="white")
        self.calc_time_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# 3D Plot Frame to visually display the flightpath
        self.plot_frame = tk.Frame(self.bg_canvas, bg="#650c00", bd=2, relief="groove")
        self.plot_frame.place(relx=0.5, rely=0.96, anchor="s", width=500, height=300)
        self.figure = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.draw()
        input_frame.columnconfigure(1, weight=1)

# Create windows
        self.bg_canvas.create_window(400, 100, window=tk.Label(self.bg_canvas, text="NavCubierre Navigation System", font=("FreeMono", 18, "bold"), background="#650c00", foreground="white"), anchor="center")
        self.bg_canvas.create_window(200, 200, window=input_frame, anchor="center")
        self.bg_canvas.create_window(600, 200, window=result_frame, anchor="center")
        self.star_points = {}

# calculates the distance that the user sees when inputting the origin and destination star.
    def star_selection(self):
        origin = self.origin_star.get()
        destination = self.destination_star.get()

        if not all([origin, destination]):
            self.distance.set("")
            self.calculate_button.config(state="disabled")
            return

        if origin not in self.star_data or destination not in self.star_data:
            self.distance.set("")
            messagebox.showerror("Error", "Origin or destination star not found in database.")
            self.calculate_button.config(state="disabled")
            return

        origin_data = self.star_data[origin]
        destination_data = self.star_data[destination] # Changed dest to destination
        distance = np.sqrt(
            (destination_data['x'] - origin_data['x']) ** 2 +
            (destination_data['y'] - origin_data['y']) ** 2 +
            (destination_data['z'] - origin_data['z']) ** 2
        )
        self.distance.set(f"{distance:.2f}")
        self.calculate_button.config(state="normal")

    def calc_selection(self): # Changed _calculate_combined to calc_selection
        origin = self.origin_star.get()
        destination = self.destination_star.get()
        self.calculate_button.config(state="disabled")
        result = self.run_fortran(origin, destination)
        self.process_result(result)
        self.calculate_button.config(state="normal")

    def run_fortran(self, origin, destination):
        origin_data = self.star_data[origin]
        destination_data = self.star_data[destination]
# In case the fortran executable is not dowloaded with the initial file:
        try:
            command = [
                self.fortran_executable,
                str(origin_data['x']), str(origin_data['y']), str(origin_data['z']),
                str(destination_data['x']), str(destination_data['y']), str(destination_data['z']),
            ]
            print(f"Running Fortran command: {command}")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            output_lines = output.decode().splitlines()
            error_output = error.decode()
            return ("success", output_lines)
        except FileNotFoundError:
            error_message = f"Fortran executable not found at {self.fortran_executable}.  Please check the path."
            print(error_message)
            return ("error", error_message)

    def process_result(self, result):
        if result[0] == "error":
            messagebox.showerror("Error", result[1])
        elif result[0] == "success":
            output_lines = result[1]
            distance_line = next((line for line in output_lines if "Distance:" in line), None)
            time_line = next((line for line in output_lines if "Total Time:" in line), None)
            if distance_line and time_line:
                distance_pc = float(distance_line.split(":")[1].strip())
                total_time_years = float(time_line.split(":")[1].strip())
                self.distance.set(f"{distance_pc:.2f}")
                self.total_time.set(f"{total_time_years:.2f}")
# Calculations to plot the path (visual only)
                origin_name = self.origin_star.get()
                destination_name = self.destination_star.get()
                origin_data = self.star_data[origin_name]
                destination_data = self.star_data[destination_name]
                num_points = 100  # Number of points to calculate for the path
                x = np.linspace(origin_data['x'], destination_data['x'], num_points)
                y = np.linspace(origin_data['y'], destination_data['y'], num_points)
                z = np.linspace(origin_data['z'], destination_data['z'], num_points)
                self.trajectory(x, y, z, origin_name=origin_name, destination_name=destination_name, distance=distance_pc) #added distance

    def trajectory(self, x, y, z, origin_name, destination_name, distance): #added distance
        origin_data = self.star_data[origin_name]
        destination_data = self.star_data[destination_name]
        trajectory_dist = np.sqrt((destination_data['x'] - origin_data['x']) ** 2 + (destination_data['y'] - origin_data['y']) ** 2 + (destination_data['z'] - origin_data['z']) ** 2)
        self.ax.clear()
        self.ax.set_xlabel('X (parsecs)')
        self.ax.set_ylabel('Y (parsecs)')
        self.ax.set_zlabel('Z (parsecs)')
        self.ax.set_title(f'Trajectory from {origin_name} to {destination_name}, Distance: {trajectory_dist:.2f} pc')
# Plot origin and destination stars
# Ensures that if the spectral type is not given, star will be plotted in gold color
        if origin_name not in self.star_points:
            self.star_points[origin_name] = self.ax.scatter(origin_data['x'], origin_data['y'], origin_data['z'], c=origin_data['color'], marker='*', s=100, label=f"{origin_name} (Origin)")
        else:
            self.star_points[origin_name].set_data(np.array([origin_data['x']]), np.array([origin_data['y']]))
            self.star_points[origin_name].set_3d_properties(np.array([origin_data['z']]))

        if destination_name not in self.star_points:
            self.star_points[destination_name] = self.ax.scatter(destination_data['x'], destination_data['y'], destination_data['z'], c=destination_data['color'], marker='*', s=100, label=f"{destination_name} (Destination)")
        else:
            self.star_points[destination_name].set_data(np.array([destination_data['x']]), np.array([destination_data['y']]))
            self.star_points[destination_name].set_3d_properties(np.array([destination_data['z']]))
# Plot the flightpath
        self.path_line, = self.ax.plot(x, y, z, 'r-', lw=2)
        self.ax.legend()
        self.canvas.draw()

# In case the window needs to be/is forced closed
    def on_close(self):
        self.stop_flag = True
        self.destroy()

if __name__ == "__main__":
    star_data_for_plotting = load_star_data()
    if not star_data_for_plotting:
        print("Error: Could not load star data. Exiting.")
        sys.exit()
    app = NavCubierreGUI(star_data_for_plotting)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
