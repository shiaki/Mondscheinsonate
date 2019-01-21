# Mondscheinsonate

Sample script for lunar eclipse HDR photography.

![Running](/images/DSC00004.png?raw=true "Running")
![Running](/images/DSC00025.png?raw=true "Running")
*Figure 1*: Jan 21, 2019 lunar eclipse. The weather was poor so I did not get a good shot.

Dependencies:
- libgphoto2 (v2.5.4-1)
- python-gphoto2 (v1.9.0)
- numpy (v1.15.4)
- scipy (v1.2.0)
- [Optional] matplotlib (v3.0.2)

Tested for:
- Raspberry Pi 3 Model B+ (Raspbian Nov 2018, Kernel v4.14, Python 3.6)
- Sony A7rII (Firmware: v3.30)
- Sigma MC-11 Mount Converter
- Canon EF 400mm f/5.6L USM

You may modify this script to fit your camera / lens / computer.
However, please note that every camera is different, and the approach used
here may not represent the best practice.

**Please use at your own discretion.**

Script generation: `magnitude.py`
Camera control: `ecl.py`
