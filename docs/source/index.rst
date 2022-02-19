.. 

Elliptec: Simple control of Thorlabs Elliptec devices
======================================================

ThorLabs Elliptec devices offer a neat way to quickly set up automated workflows in optical systems. This project aims to provide a simple and quick way to control them directly from Python. It uses the pyserial_ library and is inspired by the TL-rotation-control_ project by `Chris Baird`_. The end goal of the project is to reproduce the entire functionality of the official `Elliptec Software`_. 

.. _pyserial: https://github.com/pyserial/pyserial
.. _TL-rotation-control: https://github.com/cdbaird/TL-rotation-control
.. _Chris Baird: https://github.com/cdbaird
.. _Elliptec Software: https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ELL

**This library is still under active development. Serious bugs are present and breaking changes will be introduced.** 

Basic examples
==============

A basic example, which shows how to use a shutter:

.. code-block:: python
   
   import elliptec
   controller = elliptec.Controller('COM3')
   sh = elliptec.Shutter(controller)
   # Get information about the device
   info = sh.get('info')
   # Home the shutter before usage
   sh.home()
   # Open shutter, acquire, and close again
   sh.open()
   # ... acquire or perform other tasks
   sh.close()

An example using a rotator to collect multiple polarizations:

.. code-block:: python
   
   import elliptec
   controller = elliptec.Controller('COM3')
   ro = elliptec.Rotator(controller)
   # Home the rotator before usage
   ro.home()
   # Loop over a list of angles and acquire for each
   for angle in [0, 45, 90, 135]:
       ro.set_angle(angle)
   # ... acquire or perform other tasks

An example using a four-positional slider:

.. code-block:: python

   import elliptec
   controller = elliptec.Controller('COM3')
   sl = elliptec.Slider(controller)
   # Home the slider before usage
   sl.home()
   # Move slider to position 3
   sl.set_slot(3)
   # Move slider forward (to position 4)
   sl.move('forward')

Advanced examples
=================

An advanced example, which shows how to control multiple devices plugged into one ELLB bus controller simultaneously. The example assumes you have a shutter and a rotator on addresses 0 and 1 respectively, and shows how to take two images in perpendicular polarizations:

.. code-block:: python
   
   import elliptec
   controller = elliptec.Controller('COM4')

   sh = elliptec.Shutter(controller, address='0')
   ro = elliptec.Rotator(controller, address='1')
   # Home the shutter and the rotator
   sh.home() 
   ro.home()
   # Loop over a list of angles and opne/acquire/close for each
   for angle in [0, 90]:
       ro.set_angle(angle)
       # Open shutter, acquire, and close again
       sh.open()
       # ... acquire or perform other tasks
       sh.close()

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
