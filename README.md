# qlab

qlab is a Python package that provides methods useful to the Quantum Information Lab @ La Sapienza.

It was developed to conduct the experiments of my MSc thesis.

This is __not__ an official package from the group.

It currently features:
  - A method to evaluate the permanent of a numpy matrix using Ryser's formula.
  This is a fork of Pete Shadbolt's [repository](https://github.com/peteshadbolt/permanent), updated to work with Python 3.6.
  - A controller for the Leoni FiberSwitch© series.
  - A controller for the Keithley 2231A DC Power Supplies.
  - An updated version of Michael Leung's [PyAPT](https://github.com/mcleung/PyAPT), that works with Python 3.6.
  - A controller for the ID Quantique ID800 TDC.
  - An helper function to plot and fit Hong-Ou-Mandel experiments.

## Requirements

qlab requires [pyvisa](https://github.com/pyvisa/pyvisa) to interface with some instruments. pyvisa is installaed automatically when qlab is installed.

pyvisa, in turns, uses NI-Visa, which can be downloaded from [National Instruments' website](http://www.ni.com/visa/) by creating a free account.

NI-Visa is required __only__ by the `KeithleyPowerSupply` and the `LeoniFiberSwitch` classes, to use the rest of the package it is not strictly needed.

PyAPT requires ThorLabs' APT drivers, which can be downloaded from their [website](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=Motion_Control). You will then need to copy `APT.dll` and `APT.lib` inside `qlab/controllers` directory.

ID Quantique dll libraries are provided with the ID800. Specifically you need to copy `tdcbase.dll` (along with `tdcbase.lib` and `libusb0.dll`) inside `qlab/controllers` directory, or point to it when creating an `IDQ800` object.

## Install

qlab is available on [PyPI](https://pypi.python.org/), so it can be easily installed with
```
pip install qlab
```
