"""The Elliptec Python Library"""
from .cmd import commands
from .devices import devices
from .errors import ExternalDeviceNotFound
from .scan import find_ports, scan_for_devices
from .tools import is_null_or_empty, parse, s32, error_check, move_check

# Classes for controllers
from .controller import Controller

# General class for all motors
from .motor import Motor

# Individual device implementations
from .shutter import Shutter
from .slider import Slider
from .rotator import Rotator
from .linear import Linear
from .iris import Iris

__all__ = [
    "commands",
    "devices",
    "ExternalDeviceNotFound",
    "Controller",
    "Motor",
    "Shutter",
    "Slider",
    "Rotator",
    "Linear",
    "Iris",
    "find_ports",
    "scan_for_devices",
    "is_null_or_empty",
    "parse",
    "s32",
    "error_check",
    "move_check",
]
