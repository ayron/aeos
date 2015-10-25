# aeos
Ayron's Earth Orbit Simulator

## Goal
A high-fidelity space-craft/space mission simulator.
 - Orbit/attitude propogration
 - Sensor/Actuator/Comms simulation
 - Interface for control software
 - Useful UI (I currently envision something like a combination of STK and Matlab)
 - Command line interface for integration with other programs/scripting.
 
## Current State
 - Only orbit propogation (Simple Newtonian Gravity).
 - PyQt/VTK UI.
   - Can setup up and visualize simulation.

## TODO
 - Transformation between Keplarian/Cartesian coordinates.
 - GCRF/ITRF transformation
 - J2 and WGS86 gravity model.
 - Sun, Moon gravity
 - Air drag, solar pressure
 - Attiude dynamics
 - Interface to control software
 - Add python scripting/console interface to UI
 - Attitude visualization
 - Graphing integration
 - ...
 
## Why
For practice and for fun.

## Dependencies
PyQt
VTK
Python
Eigen
