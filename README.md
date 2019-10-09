# RngKit
Thiagojm  
tjm.plastica@gmail.com    
Written in Python 3.7.4  
-----------------------

# ABSTRACT

This project represents my puttering around with hardware entropy sources and
random number generation in Windows, to help to our project of mind matter interaction.

Kit for working with TRNGs (True Random Number Generators), creating Z-score tables, acquiring data and LivePlot!

# PyInstaller  

To make executable with pyinstaller:
pyinstaller --noconsole --hidden-import=PIL._tkinter_finder rngkit.py

Then copy files in this folder to the /dist/rngkit folder.
