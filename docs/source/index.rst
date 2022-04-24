.. 

Elliptec: Simple control of Thorlabs Elliptec devices
======================================================

ThorLabs Elliptec devices offer a neat way to quickly set up automated workflows in optical systems. This project aims to provide a simple and quick way to control them directly from Python. It uses the pyserial_ library and is inspired by the TL-rotation-control_ project by `Chris Baird`_. The end goal of the project is to reproduce the entire functionality of the official `Elliptec Software`_. 

.. _pyserial: https://github.com/pyserial/pyserial
.. _TL-rotation-control: https://github.com/cdbaird/TL-rotation-control
.. _Chris Baird: https://github.com/cdbaird
.. _Elliptec Software: https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ELL

💣 **This library is still under active development. Serious bugs are present and breaking changes will be introduced.** 

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

An example using a rotator (mount or stage) to collect multiple polarizations/angles:

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

An example using a linear stage to find optimal focus:

.. code-block:: python

   import elliptec
   controller = elliptec.Controller('COM3')
   ls = elliptec.Linear(controller)
   # Home the linear stage before usage
   ls.home()
   # Loop over a list of positions and measure gain for each
   for distance in range(0, 61, 10):
   ls.set_distance(distance)
   # ... measure gain

Advanced examples
=================

An advanced example, which shows how to control multiple devices plugged into one ELLB bus controller simultaneously. The example assumes you have a shutter and a rotator on addresses 1 and 2 respectively, and shows how to take two images in perpendicular polarizations:

.. code-block:: python
   
   import elliptec
   controller = elliptec.Controller('COM4')
   sh = elliptec.Shutter(controller, address='1')
   ro = elliptec.Rotator(controller, address='2')
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

If you haven't changed the addresses of your boards, you can either do so through the `Elliptec Software`_, or by connecting them one-by-one to the bus and using the ``change_address()`` function of a device. Assuming a ``PC -> controller -> bus`` connecion, the setup would look something like this:

.. code-block:: python

   import elliptec
   controller = elliptec.Controller('COM4')
   # connect your first device to the bus
   device_1 = elliptec.Motor(controller)
   device_1.change_address('1')
   # connect your second device
   device_2 = elliptec.Motor(controller)
   device_2.change_address('2')


The changes made to the addresses should last until the bus loses power, at which point all devices might revert to an address of 0.

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
