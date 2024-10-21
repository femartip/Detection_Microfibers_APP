import sys
import PyInstaller.__main__

system = sys.platform

if system == "linux":
    PyInstaller.__main__.run([
        'main.py',
        '--distpath=./linux_build/dist',
        '--workpath=./windows_build/build',
        '--specpath=./linux_build',
        '--noconfirm',
        '--name=MicroFiberDetect',
        '--windowed',
        '-i=../images/icon.ico',
    ])
    #pyinstaller main.py --distpath ./linux_build/dist --workpath ./linux_build/build --noconfirm --specpath ./linux_build --name Detector_fibras --add-data ../modules/*.py:./modules/ --add-data ../models/model.ts:. --collect-all torch --collect-all torchvision --collect-all numpy --collect-all opencv-python
elif system == 'win32':
    PyInstaller.__main__.run([
        'main.py',
        '--distpath=./windows_build/dist',
        '--workpath=./windows_build/build',
        '--noconfirm',
        '--specpath=./windows_build',
        '--name=MicroFiberDetect',
        '--windowed',
        '-i=../images/icon.ico',
    ])

    #pyinstaller main.py --distpath ./windows_build/dist --workpath ./windows_build/build --noconfirm --specpath ./windows_build --name Detector_fibras --windowed --add-data ../modules/*.py:./modules/ --add-data ../models/*:./models --collect-all torch --collect-all torchvision --collect-all libtorch --collect-all torchvision --collect-all numpy --collect-all opencv-python