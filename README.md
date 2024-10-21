# Micro Fiber Detection in Sludge

## Project Description

This project contains an application that is designed to detect micro fibers in sludge.

Structure:

- Utils -
- images - Containes all images used in the app
- models - Torchscript file for bothe CA and Glass models
- modules - code file
- test_data - Contains sample images extracted from glass filter.
- themes - app stylesheet
- widgets -
- main.py - main file of app
- main.ui - ui file for qtdesigner

## Table of Contents

1. Installation
2. Usage
3. Features
4. Contributing
5. License

## Installation

### Source Code

#### Prerequisites

- Python 3
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

https://drive.google.com/file/d/10oMat7ValwrEglhZC1f1nt1y8SrFx-be/view?usp=sharing

After downloading the application, extract the files and run the executable file.

Note that Windows Defender may block the application from running. To run the application, click on "More info" and then "Run anyway".

## Usage

![image](https://github.com/femartip/Detection_Microfibers_APP/assets/99536660/81a4f3b7-5168-4983-8f10-b1a74572c697)
![image](https://github.com/femartip/Detection_Microfibers_APP/assets/99536660/40a2f57d-9ecd-44fa-8a2d-1fed463c2fa8)
![image](https://github.com/femartip/Detection_Microfibers_APP/assets/99536660/6c09ec44-6b27-4db6-b2e5-539f861d8c17)

## Features

✔️ Implemented features:

- Windows build
- Carbonated active filter model for detecion
- Glass fiber filter model for detection
- Image processing
- Progress bar for image processing
- Overlay bounding box on detected fibers
- Total fiber count
- Fiber count per image
- Fiber length measurement at defined scale
- Fiber approximated color. Implemented with K-means clustering (Previous version used an approximation based on HSL color space.)
- Export table data to csv
- Export image with bounding box
- Home page explanation of app
- Cuda support

❌ Features to be implemented:

- Linux build
- Mac build
- Export images at original resolution
- Make segmentation and bounding box toggleable

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

MIT License

Copyright (c) 2024 Felix Marti Perez
