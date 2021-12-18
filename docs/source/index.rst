.. 

Elliptec: Simple control of Thorlabs Elliptec devices
======================================================

ThorLabs Elliptec devices offer a neat way to quickly set up automated workflows in optical systems. This project aims to provide a simple and quick way to control them directly from Python. It uses the pyserial_ library and is inspired by the TL-rotation-control_ project by `Chris Baird`_. The end goal of the project is to reproduce the entire functionality of the official `Elliptec Software`_. 

.. _pyserial: https://github.com/pyserial/pyserial
.. _TL-rotation-control: https://github.com/cdbaird/TL-rotation-control
.. _Chris Baird: https://github.com/cdbaird
.. _Elliptec Software: https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ELL

**This library is still under active development. Serious bugs are present and breaking changes will be introduced.** 

A basic example, which shows how to use a shutter:::

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

An example using a rotator to collect multiple polarizations:::

   import elliptec
   ro = elliptec.Rotator('COM3')
   # Home the rotator before usage
   ro.home()
   # Loop over a list of angles and acquire for each
   for angle in [0, 45, 90, 135]:
   ro.set_angle(angle)
   # ... acquire or perform other tasks

An example using a four-positional slider:::

   import elliptec
   sl = elliptec.Slider('COM3')
   # Home the slider before usage
   sl.home()
   # Move slider to position 3
   sl.set_slot(3)
   # Move slider forward (to position 4)
   sl.move('forward')


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
