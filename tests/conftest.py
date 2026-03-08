"""Shared fixtures for elliptec tests."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def make_info_response(motor_type: int = 14, pulse_per_rev: int = 32768, range_: int = 360, serial_no: str = "12345678") -> dict:
    """Create a canned info dict matching what parse() returns for an IN response."""
    return {
        "Address": "0",
        "Motor Type": motor_type,
        "Serial No.": serial_no,
        "Year": "2023",
        "Firmware": "01",
        "Thread": "Metric",
        "Hardware": "1",
        "Range": range_,
        "Pulse/Rev": pulse_per_rev,
    }


@pytest.fixture
def mock_controller():
    """A Controller with a mocked serial port. Does not open any real ports."""
    with patch("elliptec.controller.serial.Serial") as mock_serial_cls:
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_cls.return_value = mock_serial

        from elliptec.controller import Controller

        ctrl = Controller(port="/dev/fake", debug=True)
        yield ctrl
