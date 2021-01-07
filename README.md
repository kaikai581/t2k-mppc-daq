# FEBDAQMULTx2
A dual board automated DAQ system for QA/QC of [Multi-Pixel Photon Counters (MPPC)](https://www.hamamatsu.com/us/en/product/optical-sensors/mppc/what_is_mppc/index.html).

## About The Project
This project consists of 2 software GUI applications that control 5 hardware components. Below is an overview of all subsystems involved in this project.

### Hardware Components
The hardware components this project aims to control are
* A PCB with 64 MPPCs

  This is the subject to study, and is not directly controlled by the software.
* Two CAEN [DT5702](https://www.caen.it/products/dt5702/) front-end board (FEB) modules

  Each FEB has 32 channels. With two boards working together, 64-channel data can be taken at one shot.
* Agilent (now Keysight) [N6700B](https://www.keysight.com/en/pd-838422-pn-N6700B/low-profile-modular-power-system-mainframe-400w-4-slots?cc=CA&lc=fre) Power System
* Tektronix [AFG3252](https://www.tek.com/datasheet/afg3000-series) Arbitrary/Function Generator
* Thermo Scientific [NESLAB RTE 10](https://www.marshallscientific.com/Thermo-Neslab-RTE-10-Circulating-Chiller-p/th-nerte10.htm) Bath/Circulator
* Five temperature sensors with a control unit interfaced through RS-232

### Hardware Setup
The power system supplies a bias voltage to all 64 MPPCs through an interface board. The interface board and the MPPC PCB are connected through SAMTEC flat cable system, which both the bias voltage and signals from MPPCs run through.
Two CAEN FEBs are each connected to interface boards for signal readout.
The FEBs, power system, and function generator are connected to an unabridged ethernet switch, which in turn is connected to a host computer for remote control. The water circulator and the temperature sensors, on the other hand, communicate with the host computer through RS-232.

### Software Components

This project contains two software GUI applications developed on a host computer with Ubuntu 18.04 LTS as the OS.

* The main DAQ application for FEB configuration and control of data acquisition

  The development philosophy of this app is trying to be a minimal two-board extension to the [reference DAQ](https://www.caen.it/download/?filter=DT5702) written in C++/ROOT for a single board provided by CAEN.

* A slow control app for all other instrument

  Including the power system, function generator, water circulator, and temperature sensors. This app is written in python/PyQT.

### Software Communication

To ease the layout on the DAQ GUI, and use the slow control app on its own, the slow control functions are separated from the main DAQ and made standalone. This modular design comes with an expense, i.e., passing information between the two apps. Thanks to the simple and popular messaging library, [ZeroMQ](https://zeromq.org/), and its comprehensive language bindings, inter-process communication between the two apps was implemented without too much hassle.

## Software Installation

### Anaconda as the Library Manager
[Anaconda](https://www.anaconda.com/) is one of the most popular cross-platform python distributions. With its third-party repositories, such as conda-forge, Anaconda turns into a generic package repository, suitable for users without root permission to install library dependencies for their projects.

This project adopts Anaconda as the library manager for portability and versatility.

### Dependency Installation
Download [Anaconda installer](https://www.anaconda.com/products/individual) corresponding to your operating system. Follow the [instructions](https://docs.anaconda.com/anaconda/install/) to install Anaconda on your host system.

Once a working `conda` command exists on your system, follow the steps to install dependencies.
1. Create and activate an environment.
  ```
  conda create -n daq
  conda activate daq
  # add the third-party channel conda-forge with priority
  conda config --env --add channels conda-forge
  ```
2. Install the following packages with `conda`.
  ```
  conda install root cppzmq pyqt pyserial pyqtgraph pandas
  ```
3. Still, some libraries are not packaged in Anaconda. Fortunately, they are available through `pip`.
  ```
  pip install python-vxi11
  ```

Note that it could happen that the project cannot run with arbitrary combinations of all package versions. [Here](https://github.com/kaikai581/t2k-mppc-daq/blob/master/FEBDAQMULTx2/pkg_ver.txt) I provide a snapshot of a combination of all package versions that guarantees to run the applications.

### Project Installation and Execution
1. Clone this repository with your conda environment activated.
  ```
  git clone https://github.com/kaikai581/t2k-mppc-daq.git
  ```
2. Bring up the main DAQ GUI under superuser (yes, sorry, I do not keep my promise) by the command.
  ```
  cd FEBDAQMULTx2/DAQ
  root -l 'FEBDAQMULT.C+("enp0s31f6")'
  ```
  Here, `enp0s31f6` is the name of the ethernet port connected to the unabridged switch. It can be obtained by executing `ifconfig` on the command line.

3. To bring up the slow control app, simply click the "Slow Control" button on the bottom left of the DAQ GUI.

## Change Log
On 20200827 I merged my test repo into my production repo to reduce repo redundancy. This project should be fine to be fully open.

## t2k-mppc-daq-private

This repository stores code that is not supposed to be freely accessible to the
public.
Currently the sample DAQ code for CAEN DT5702 is stored for my own reference.

## t2k-mppc-daq
Code for 64-channel T2K MPPC DAQ, which involves several instrument to control.
