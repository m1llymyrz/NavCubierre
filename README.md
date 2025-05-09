# NavCubierre
Final Project for University of Wyoming's Mathematical Computational Physics 2 course

# Introduction
NavCubierre is a theoretical navigation software meant for interstellar warp drives, such as an Alcubierre drive, which NavCubierre was named after. This navigation system provides users with an optimized fuel flightplan when travelling between stars. The flightplan is then displayed, with the origin star situatied at the origin of a 3d graph, and the destination star displayed at it's coordinates. The visual display is as accurate as possible- using the real color magnitudes of the chosen stars as the display color.  

## Relativity and assumtions
There were a few key assumptions made with this project that impact the real-world application of this navigation system. That being said, Alcubierre drives are pureley theoretical themselves and break the laws of physics. NavCubierre ignores relativity and displays travel times in proper time, rather than in dilated time. This assumption was made due to the nature of the Alcubierre drive.

Alcubierre drives work by creating a "space-time bubble" around the spacecraft. This bubble warps the fabric of space-time in front of the ship down, and warps the space-time fabric behind the ship up. This method makes a "space-time wave" that the ship can ride on, and allows the ship to travel faster than the speed of light. 
Typically when objects move at relativistic speeds (i.e. at or near the speed of light), time is dilated. Time moves slower for people moving at a relativistic speed, rather than for someone not moving at a relativistic speed. Since NavCubierre shows users a time optimized path, dilated time was neglected for this travel time.

## Base Mathematics
In order to find the optimized fuel path, the euler-lagrange equation was used to give us equations of motion for the spacecraft, then these equations were approximated using 4th order runge-kutta. The inputs from the python code are transfered to the fortran code, where the euler-lagrange equation was approximated, then solved for time.

# Required Packages and Data
Fortran and python capabilities are required for this software. 

## Fotran installation:
To install fortran, in the terminal execute the command:
  sudo apt-get install gfortran

## Required Python3 packages
This code was written using python3.12. It has not been tested on a python interface that is not python3. This code requires the python packages numpy, matplotlib, ktinter, mpl_toolkits.mplot3d, and matplotlib.backends.backend_tkag. Most of these come standard with a regular python3 download, but in case you need install these packaged, execute the following commands.

If you do not have an enviroment set up:
  sudo apt/get install python3-<package_name>
Or if you have an environment set up:
  pip install python3-<package_name>

Note that to install kniter, the package name is tk. 

A csv file from the website https://www.astronexus.com/projects/hyg is also required for this software to run. Download this file seperatley and move it into the same folder as your main NavCubierre code and fortran code. Downloading the 2024 version is reccommended. 

# Installation
Download the entire NavCubierre folder and move this folder into your desired local repository. You'll then need to compile the fortran code and make the python code executeable. A large datafile is required for this software to run. It is available at https://www.astronexus.com/projects/hyg where it's reccommended to download the 2024 file version. 

In order for this code to run, the downloaded data file must be in the same repository as your other code. 

# Test Case
     ![alt text](C:\Users\ameli\Downloads\Screenshot 2025-05-09 151034.png)

# Troubleshooting

