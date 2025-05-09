#!/usr/bin/env python3.12

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys, os

# Load star data
def ld_sd(fname="hygdata_v41.csv"):
    s_data = {}
    dat = np.loadtxt(fname, dtype=str, delimiter=',', skiprows=1, usecols=(6, 17, 18, 19, 15)) #using coloumn 15 to graph real star colors was an afterthought
    # load in the star name, spectral type, x, y, and z coordinate
    for r in dat:
        n = r[0].strip()
        x_coord = float(r[1].strip())
        y_coord = float(r[2].strip())
        z_coord = float(r[3].strip())
        s_type = r[4].strip().upper()
        col = c2st(s_type)
        s_data[n] = {'x': x_coord, 'y': y_coord, 'z': z_coord, 'spectral_type': s_type, 'color': col}
    return s_data

# Find star color from spectral type; used only for visual graphing
def c2st(stype):
    stype = stype.strip().upper()
    if stype.startswith("O"):
        return 'slateblue'
    elif stype.startswith("B"):
        return 'lightskyblue'
    elif stype.startswith("A"):
        return 'white'
    elif stype.startswith("F"):
        return 'yellow'
    elif stype.startswith("G"):
        return 'orange'
    elif stype.startswith("K"):
        return 'red'
    elif stype.startswith("M"):
        return 'darkred'
    else:
        return 'gold'

class NavGUI(tk.Tk):
    def __init__(self, s_data):
        super().__init__()
        self.title("NavCubierre Navigation System")
        self.geometry("800x600")
        self.orig_star = tk.StringVar()
        self.dest_star = tk.StringVar()
        self.dist = tk.StringVar()
        self.ttime = tk.StringVar()
        self.s_data = s_data
        self.s_names = sorted(list(self.s_data.keys()))
        self.bg_canv = tk.Canvas(self, highlightthickness=0, bg="#650c00")
        self.bg_canv.pack(fill="both", expand=True)
        self._bg_lines()
        self._create_widgets()
        self.lift()
        self.f_exec = "./runge_fuel.exe" # fortran executable set here
        self.stop_flg = False
        self.path_ln = None  # To store the plotted path

    def _bg_lines(self): # Used to make the grid pattern in the background
        l_color = "#e67e22"
        sp = 20
        for i in range(0, 600, sp):
            self.bg_canv.create_line(0, i, 1000, i, fill=l_color)
        for i in range(0, 800, sp):
            self.bg_canv.create_line(i, 0, i, 1000, fill=l_color)

# Creates dropdown widget and results display widget.
    def _create_widgets(self):
# Input Frame where users can access the combobox:
        in_frame = tk.Frame(self.bg_canv, bg="#650c00", bd=2, relief="groove")
        star_fields = [ {"label": "Origin Star:", "variable": self.orig_star, "combobox": None, "row": 1},
                            {"label": "Destination Star:", "variable": self.dest_star, "combobox": None, "row": 2}, ]
# here is where the combobox with a search function is implemented:
        def mk_star_field(config):
            lab = tk.Label(in_frame, text=config["label"], background="#650c00", foreground="white")
            lab.grid(row=config["row"], column=0, padx=5, pady=5, sticky="w")
            combo = ttk.Combobox(in_frame, textvariable=config["variable"], values=self.s_names, width=25)
            combo.grid(row=config["row"], column=1, padx=5, pady=5, sticky="ew")
            config["combobox"] = combo
            def on_combo_change(event): # Changed combobox to on_combobox_change
                sel_star = combo.get()
                config["variable"].set(sel_star)
                self._star_sel() # Changed update_selection to star_selection
            combo.bind("<<ComboboxSelected>>", on_combo_change)
            def auto_comp(event):
                val = combo.get()
                new_vals = [item for item in self.s_names if val.lower() in item.lower()]
                combo['values'] = new_vals if val else self.s_names
            combo.bind('<KeyRelease>', auto_comp)
            config["combobox"] = combo

        for f_config in star_fields:
            mk_star_field(f_config)

# Creates calculate button displayed with the dropdown menus
        self.calc_btn = tk.Button(in_frame, text="Calculate", command=self._calc_sel)
        self.calc_btn.grid(row=3, column=0, columnspan=2, pady=10)

# Result frame that shows users the time and distance calculated
        res_frame = tk.Frame(self.bg_canv, bg="#650c00", bd=2, relief="groove")
        self.res_frame = res_frame
        tk.Label(res_frame, text="Calculated Distance (pc):", background="#650c00", foreground="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.calc_dist_lab = tk.Label(res_frame, textvariable=self.dist, width=20, bg="white")
        self.calc_dist_lab.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(res_frame, text="Estimated Travel Time (years):", background="#650c00", foreground="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.calc_time_lab = tk.Label(res_frame, textvariable=self.ttime, width=20, bg="white")
        self.calc_time_lab.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# 3D Plot Frame to visually display the flightpath
        self.plot_frame = tk.Frame(self.bg_canv, bg="#650c00", bd=2, relief="groove")
        self.plot_frame.place(relx=0.5, rely=0.96, anchor="s", width=500, height=300)
        self.fig = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax_3d = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.draw()
        in_frame.columnconfigure(1, weight=1)

# Create windows
        self.bg_canv.create_window(400, 100, window=tk.Label(self.bg_canv, text="NavCubierre Navigation System", font=("FreeMono", 18, "bold"), background="#650c00", foreground="white"), anchor="center")
        self.bg_canv.create_window(200, 200, window=in_frame, anchor="center")
        self.bg_canv.create_window(600, 200, window=res_frame, anchor="center")
        self.star_pts = {}

# calculates the distance that the user sees when inputting the origin and destination star.
    def _star_sel(self):
        o = self.orig_star.get()
        d = self.dest_star.get()

        if not all([o, d]):
            self.dist.set("")
            self.calc_btn.config(state="disabled")
            return

        if o not in self.s_data or d not in self.s_data:
            self.dist.set("")
            messagebox.showerror("Error", "Origin or destination star not found in database.")
            self.calc_btn.config(state="disabled")
            return

        o_data = self.s_data[o]
        d_data = self.s_data[d] # Changed dest to destination
        d_val = np.sqrt(
            (d_data['x'] - o_data['x']) ** 2 +
            (d_data['y'] - o_data['y']) ** 2 +
            (d_data['z'] - o_data['z']) ** 2
        )
        self.dist.set(f"{d_val:.2f}")
        self.calc_btn.config(state="normal")

    def _calc_sel(self): # Changed _calculate_combined to calc_selection
        o = self.orig_star.get()
        d = self.dest_star.get()
        self.calc_btn.config(state="disabled")
        res = self._run_fortran(o, d)
        self._process_res(res)
        self.calc_btn.config(state="normal")

    def _run_fortran(self, o, d):
        o_data = self.s_data[o]
        d_data = self.s_data[d]
# In case the fortran executable is not dowloaded with the initial file:
        try:
            cmd = [
                self.f_exec,
                str(o_data['x']), str(o_data['y']), str(o_data['z']),
                str(d_data['x']), str(d_data['y']), str(d_data['z']),
            ]
            print(f"Running Fortran command: {cmd}")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            out_lines = out.decode().splitlines()
            err_out = err.decode()
            return ("success", out_lines)
        except FileNotFoundError:
            err_msg = f"Fortran executable not found at {self.f_exec}. Please check the path."
            print(err_msg)
            return ("error", err_msg)

    def _process_res(self, res):
        if res[0] == "error":
            messagebox.showerror("Error", res[1])
        elif res[0] == "success":
            out_lines = res[1]
            dist_line = next((line for line in out_lines if "Distance:" in line), None)
            time_line = next((line for line in out_lines if "Total Time:" in line), None)
            if dist_line and time_line:
                dist_pc = float(dist_line.split(":")[1].strip())
                time_yrs = float(time_line.split(":")[1].strip())
                self.dist.set(f"{dist_pc:.2f}")
                self.ttime.set(f"{time_yrs:.2f}")
# Calculations to plot the path (visual only)
                o_name = self.orig_star.get()
                d_name = self.dest_star.get()
                o_data = self.s_data[o_name]
                d_data = self.s_data[d_name]
                n_pts = 100  # Number of points to calculate for the path
                x_vals = np.linspace(o_data['x'], d_data['x'], n_pts)
                y_vals = np.linspace(o_data['y'], d_data['y'], n_pts)
                z_vals = np.linspace(o_data['z'], d_data['z'], n_pts)
                self._plot_traj(x_vals, y_vals, z_vals, origin_name=o_name, destination_name=d_name, distance=dist_pc) #added distance

    def _plot_traj(self, x, y, z, origin_name, destination_name, distance): #added distance
        o_data = self.s_data[origin_name]
        d_data = self.s_data[destination_name]
        traj_dist = np.sqrt((d_data['x'] - o_data['x']) ** 2 + (d_data['y'] - o_data['y']) ** 2 + (d_data['z'] - o_data['z']) ** 2)
        self.ax_3d.clear()
        self.ax_3d.set_xlabel('X (parsecs)')
        self.ax_3d.set_ylabel('Y (parsecs)')
        self.ax_3d.set_zlabel('Z (parsecs)')
        self.ax_3d.set_title(f'Trajectory from {origin_name} to {destination_name}, Distance: {traj_dist:.2f} pc')
# Plot origin and destination stars
# Ensures that if the spectral type is not given, star will be plotted in gold color
        if origin_name not in self.star_pts:
            self.star_pts[origin_name] = self.ax_3d.scatter(o_data['x'], o_data['y'], o_data['z'], c=o_data['color'], marker='*', s=100, label=f"{origin_name} (Origin)")
        else:
            self.star_pts[origin_name].set_data(np.array([o_data['x']]), np.array([o_data['y']]))
            self.star_pts[origin_name].set_3d_properties(np.array([o_data['z']]))

        if destination_name not in self.star_pts:
            self.star_pts[destination_name] = self.ax_3d.scatter(d_data['x'], d_data['y'], d_data['z'], c=d_data['color'], marker='*', s=100, label=f"{destination_name} (Destination)")
        else:
            self.star_pts[destination_name].set_data(np.array([d_data['x']]), np.array([d_data['y']]))
            self.star_pts[destination_name].set_3d_properties(np.array([d_data['z']]))
# Plot the flightpath
        if self.path_ln: # Check if a line object exists
            self.path_ln.set_data(x, y)
            self.path_ln.set_3d_properties(z)
        else:
            self.path_ln, = self.ax_3d.plot(x, y, z, 'r-', lw=2)
        self.ax_3d.legend()
        self.canvas.draw()

# In case the window needs to be/is forced closed
    def on_close(self):
        self.stop_flg = True
        self.destroy()

if __name__ == "__main__":
    star_data_for_plotting = ld_sd()
    if not star_data_for_plotting:
        print("Error: Could not load star data. Exiting.")
        sys.exit()
    app = NavGUI(star_data_for_plotting)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
