"""Module for scanning for Elliptec devices."""
from __future__ import annotations

import logging

import serial as s
import serial.tools.list_ports as listports
from .controller import Controller
from .errors import ExternalDeviceNotFound
from .motor import Motor

logger = logging.getLogger(__name__)

# Scanning functions


def find_ports() -> list[str]:
    """Find all available ports with an Elliptec device connected."""
    avail_ports = []
    for port in listports.comports():
        if port.serial_number:
            try:
                connection = s.Serial(port.device)
                connection.close()
                avail_ports.append(port)
            except (OSError, s.SerialException):
                logger.warning("%s unavailable.", port.device)
    port_names = [port.device for port in avail_ports]
    return port_names


def scan_for_devices(controller: Controller, start_address: int = 0, stop_address: int = 0, debug: bool = True) -> list[dict[str, object]]:
    """Scan for devices on a controller. Returns a list of dictionaries with device info and controller object."""
    devices: list[dict[str, object]] = []
    for address in range(start_address, stop_address + 1):
        try:
            motor = Motor(controller, address=str(address), debug=debug)
            logger.info("%s, address %s: ELL%s \t(S/N: %s)", controller.port, address, motor.motor_type, motor.serial_no)
            device = {
                "info": motor.info,
                "controller": controller,
            }
            devices.append(device)
            del motor
        except ExternalDeviceNotFound:
            pass
    return devices
