# NavCubierre
Final Project for University of Wyoming's Mathematical Computational Physics 2 course, Spring 2025. 


# Introduction
NavCubierre is a theoretical navigation software meant for interstellar warp drives, such as an Alcubierre drive, which NavCubierre was named after. This navigation system provides users with an optimized fuel flightplan when travelling between stars. The flightplan is then displayed, with the origin star situatied at the origin of a 3d graph, and the destination star displayed at it's coordinates. The visual display is as accurate as possible- using the real color magnitudes of the chosen stars as the display color.  


### Relativity and assumtions
There were a few key assumptions made with this project that impact the real-world application of this navigation system. That being said, Alcubierre drives are pureley theoretical themselves and break the laws of physics. NavCubierre ignores relativity and displays travel times in proper time, rather than in dilated time. This assumption was made due to the nature of the Alcubierre drive.

Alcubierre drives work by creating a "space-time bubble" around the spacecraft. This bubble warps the fabric of space-time in front of the ship down, and warps the space-time fabric behind the ship up. This method makes a "space-time wave" that the ship can ride on, and allows the ship to travel faster than the speed of light. 
Typically when objects move at relativistic speeds (i.e. at or near the speed of light), time is dilated. Time moves slower for people moving at a relativistic speed, rather than for someone not moving at a relativistic speed. Since NavCubierre shows users a time optimized path, dilated time was neglected for this travel time.

For this code, it's assumed that this warp drive can travel at a maximum speed of 100c, with a max acceleration at 10c. 


### Base Mathematics
In order to find the optimized fuel path, the euler-lagrange equation was used to give us equations of motion for the spacecraft, then these equations were approximated using 4th order runge-kutta. The inputs from the python code are transfered to the fortran code, where the euler-lagrange equation was approximated, then solved for time.


# Required Packages and Data
Fortran and python capabilities are required for this software. NavCubierre also uses the HYG database as the list of navigable stars. The HYG database is a collection of the Hipparcos catalog, the Yale bright star catalog, and the Gliese Catalog of nearby stars. The HYG database can be downloaded from this link below. 


https://www.astronexus.com/projects/hyg


NavCubierre utilizes the 2024 database containing over 120,000 stars. For this project, NavCubierre utilizes the names and the distance (from the Earth) of the star. A csv file from the website is required for this software to run. Download this file seperatley and move it into the same folder as your main NavCubierre code and fortran code. Downloading the 2024 version is reccommended. Due to the large size of this csv file, I am unable to upload it to Github, which is why I encourage you to download the data yourself. 

### Fotran installation:
To install fortran, in the terminal execute the command:

    sudo apt-get install gfortran

### Required Python3 packages
This code was written using python3.12. It has not been tested on a python interface that is not python3. This code requires the python packages numpy, matplotlib, ktinter, mpl_toolkits.mplot3d, and matplotlib.backends.backend_tkag. Most of these come standard with a regular python3 download, but in case you need install these packaged, execute the following commands.


If you do not have an enviroment set up:

    sudo apt/get install python3-<package_name>
  
Or if you have an environment set up:

    pip install python3-<package_name>


Note that to install kniter, the package name is tk. 


# Installation
Download the entire NavCubierre folder and move this folder into your desired local repository. You'll then need to compile the fortran code and make the python code executeable. A large datafile is required for this software to run. It is available at https://www.astronexus.com/projects/hyg where it's reccommended to download the 2024 file version. 

In order for this code to run, the downloaded data file must be in the same repository as your other code. 


# Test Case
A screenshot of a test case is included within the repository. Once you have NavCubierre running, use Rigel as an origin star and EZ Aqr as the destination star. You should be able to type into the menus the names of these stars, then press your down arrow key to select them. Once the destination star is selected, the distance will be displayed. When you calculate this tst case, you should see a similar plot to the one in the testcase screenshot. 


# Troubleshooting
The HYG data occasianally has spots of missing data, in this case, your code may not run. 
