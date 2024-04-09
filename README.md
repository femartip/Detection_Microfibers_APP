# Micro Fiber Detection in Sewage

## Project Description
This project contains an application that is designed to detect micro fibers in sewage. 

## Table of Contents
1. Installation
2. Usage
3. Features
3. Contributing
4. License

## Installation

### Source Code

#### Prerequisites
- Python 3.8 or higher
- OpenCV
- PySide6
- PyQt6
- pyinstaller (for creating the executable file)
- torch
- torchvision
- numpy
- skimage

For running the application form the source code, after installing the prerequisits, 'main.py' file should be executed.

### Windows
Access the following link to download the application: 
https://drive.google.com/file/d/189KJ_GemMjQNTKEMQDvGG0DQSaV3JTnl/view?usp=sharing

After downloading the application, extract the files and run the executable file.
Note that Windows Defender may block the application from running. To run the application, click on "More info" and then "Run anyway".


## Usage


## Features
:heavy_check_mark: Implemented features:
- Windows build
- Carbonated active filter model for detecion
- Glass fiber filter model for detection
- Image processing
- Progress bar for image processing
- Overlay bounding box on detected fibers
- Total fiber count
- Fiber count per image
- Fiber length measurement at defined scale
- Fiber approximated color (still in development)
- Export table data to csv
- Export image with bounding box

:x: Features to be implemented:
- Linux build
- Mac build
- Export images at original resolution
- Make segmentation and bounding box toggleable

## Contributing
If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License
MIT License

Copyright (c) 2024 Felix Marti Perez
