<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/roesel/elliptec">
    <img src="images/logo.png" alt="Logo" width="230" height="150">
  </a>

  <h3 align="center">Elliptec</h3>

  <p align="center">
    Simple control of Thorlabs Elliptec&trade; devices.
    <br />
    <a href="https://elliptec.readthedocs.io/en/latest/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/roesel/elliptec">Get started</a>
    ·
    <a href="https://github.com/roesel/elliptec/issues">Report a bug</a>
    ·
    <a href="https://github.com/roesel/elliptec/issues">Request a feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

ThorLabs Elliptec&trade; devices offer a neat way to quickly set up automated workflows in optical systems. This project aims to provide a simple and quick way to control them directly from Python. It uses the [pyserial](https://github.com/pyserial/pyserial) library and is inspired by the [TL-rotation-control](https://github.com/cdbaird/TL-rotation-control) project by [Chris Baird](https://github.com/cdbaird). The end goal of the project is to reproduce the entire functionality of the official [Elliptec&trade; Software](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ELL). 

**This library is still under active development. Serious bugs are present and breaking changes will be introduced.** 

## Quickstart
A basic example, which shows how to use a shutter:
```python
import elliptec
sh = elliptec.Shutter('COM3')
# Get information about the device
info = sh.get('info')
# Home the rotator before usage
ro.home()
# Open shutter, acquire, and close again
sh.open()
# ... acquire or perform other tasks
sh.close()
```

An example using a rotator to collect multiple polarizations:
```python
import elliptec
ro = elliptec.Rotator('COM3')
# Home the rotator before usage
ro.home()
# Loop over a list of angles and acquire for each
for angle in [0, 45, 90, 135]:
  ro.set_angle(angle)
  # ... acquire or perform other tasks
```

An example using a four-positional slider:
```python
import elliptec
sl = elliptec.Slider('COM3')
# Home the slider before usage
sl.home()
# Move slider to position 3
sl.set_slot(3)
# Move slider forward (to position 4)
sl.move('forward')
```

## List of supported devices
Currently (somewhat) supported devices:
* Rotation Mount (ELL14) - [Thorlabs product page](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=12829) - typically used for polarization state generators
* Dual-Position Slider (ELL6) - [Thorlabs product page](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=9464) - typically used as a shutter
* Four-Position Slider (ELL9) - [Thorlabs product page](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=9464) - typically used as a filter wheel

As of right now, I do not have access to any other devices from the Elliptec&trade; family. If you are interested in controlling a device that is not on this list, feel free to reach out to me.

## What works and what doesn't
What works:
* basic movement
* getting information about the device 
* getting information about individual motors

What is missing:
* documentation
* safety (no library performed bounds checks etc)
* consistency (across methods, devices, returns, ...)
* automated discovery of devices
* adding devices by serial number
* searching for optimal motor frequencies
* (re)setting permanent parameters (home positions, motor frequencies)
* cleaning and optimization procedures

Some of the missing functionality can be performed using the official [Elliptec Software](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ELL).

## Support
If you are going to use this code in any way, **please let me know** via [email](mailto:roesel@gmail.com)/[twitter](https://twitter.com/DavidRoesel)/[issues](https://github.com/roesel/elliptec/issues) or find my contact info on [my website](https://david.roesel.cz/en/). I am working on this project in my spare time and need every piece of encouragement I can get! ;)

## Disclaimer
Thorlabs&trade; and Elliptec&trade; are registered trademarks of Thorlabs,&nbsp;Inc. This project is fully non-commercial and not affiliated with Thorlabs,&nbsp;Inc. in any capacity. 
