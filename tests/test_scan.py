"""Tests for the scan module with mocked serial ports."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from conftest import make_info_response


class TestFindPorts:
    def test_no_ports(self):
        from elliptec.scan import find_ports

        with patch("elliptec.scan.listports.comports", return_value=[]):
            assert find_ports() == []

    def test_port_with_serial_number(self):
        from elliptec.scan import find_ports

        mock_port = MagicMock()
        mock_port.serial_number = "ABC123"
        mock_port.device = "/dev/ttyUSB0"

        mock_serial = MagicMock()

        with patch("elliptec.scan.listports.comports", return_value=[mock_port]), \
             patch("elliptec.scan.s.Serial", return_value=mock_serial):
            result = find_ports()
        assert result == ["/dev/ttyUSB0"]
        mock_serial.close.assert_called_once()

    def test_port_without_serial_number(self):
        from elliptec.scan import find_ports

        mock_port = MagicMock()
        mock_port.serial_number = None
        mock_port.device = "/dev/ttyUSB0"

        with patch("elliptec.scan.listports.comports", return_value=[mock_port]):
            result = find_ports()
        assert result == []

    def test_port_serial_exception(self):
        from elliptec.scan import find_ports
        import serial

        mock_port = MagicMock()
        mock_port.serial_number = "ABC123"
        mock_port.device = "/dev/ttyUSB0"

        with patch("elliptec.scan.listports.comports", return_value=[mock_port]), \
             patch("elliptec.scan.s.Serial", side_effect=serial.SerialException):
            result = find_ports()
        assert result == []


class TestScanForDevices:
    def test_scan_finds_device(self):
        from elliptec.scan import scan_for_devices

        info = make_info_response(motor_type=14)
        mock_ctrl = MagicMock()
        mock_ctrl.port = "/dev/fake"
        mock_ctrl.send_instruction.return_value = info

        result = scan_for_devices(mock_ctrl, start_address=0, stop_address=0, debug=True)
        assert len(result) == 1
        assert result[0]["info"] == info
        assert result[0]["controller"] is mock_ctrl

    def test_scan_no_device(self):
        from elliptec.scan import scan_for_devices

        mock_ctrl = MagicMock()
        mock_ctrl.send_instruction.return_value = None

        result = scan_for_devices(mock_ctrl, start_address=0, stop_address=0, debug=True)
        assert result == []

    def test_scan_multiple_addresses(self):
        from elliptec.scan import scan_for_devices

        info = make_info_response(motor_type=14)
        mock_ctrl = MagicMock()
        mock_ctrl.port = "/dev/fake"
        # First address has device, second doesn't, third has device
        mock_ctrl.send_instruction.side_effect = [info, None, info]

        result = scan_for_devices(mock_ctrl, start_address=0, stop_address=2, debug=True)
        assert len(result) == 2
