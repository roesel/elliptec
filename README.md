<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/roesel/elliptec">
    <img src="images/logo.png" alt="Logo" width="230" height="150">
  </a>

  <h3 align="center">Elliptec</h3>

  <p align="center">
    Simple control of Thorlabs Elliptec devices.
    <br />
    <a href="https://github.com/roesel/elliptec"><strong>No docs yet »</strong></a>
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

ThorLabs Elliptec devices offer a neat way to quickly set up automated workflows in optical systems. This project aims to provide a simple and quick way to control them directly from Python. It uses the [pyserial](https://github.com/pyserial/pyserial) library and is inspired by the [TL-rotation-control](https://github.com/cdbaird/TL-rotation-control) project by [Chris Baird](https://github.com/cdbaird). The end goal of the project is to reproduce the entire functionality of the official [Elliptec Software](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ELL). 

**This library is still under active development. Serious bugs are present and breaking changes will be introduced.** 

## List of supported devices
Currently (somewhat) supported devices:
* Rotation Mount (ELL14) - [Thorlabs product page](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=12829) - typically used for polarization state generators
* Dual-Position Slider (ELL6) - [Thorlabs product page](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=9464) - typically used as a shutter
* Four-Position Slider (ELL9) - [Thorlabs product page](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=9464) - typically used as a filter wheel

As of right now, I do not have access to any other devices from the Elliptec family. If you are interested in controlling a device that is not on this list, feel free to reach out to me.

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
If you are going to use this code in any way, **please let me know** via email/twitter/issues, you can find my contact info on [my website](https://david.roesel.cz/en/). I am working on this project in my spare time and need every piece of encouragement I can get! ;)
