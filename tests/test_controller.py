"""Tests for the Controller class with mocked serial port."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from elliptec.controller import Controller


class TestControllerInit:
    def test_connect_to_port(self, mock_controller):
        """Controller stores port name on successful connection."""
        assert mock_controller.port == "/dev/fake"

    def test_connect_to_port_failure(self):
        """Controller handles SerialException gracefully."""
        import serial

        with patch("elliptec.controller.serial.Serial", side_effect=serial.SerialException):
            ctrl = Controller(port="/dev/noexist", debug=True)
        assert ctrl.port is None

    def test_search_and_connect_uses_first_port(self):
        """When no port given, Controller tries the first available port."""
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"

        mock_serial = MagicMock()
        mock_serial.is_open = True

        with patch("elliptec.controller.serial.tools.list_ports.comports", return_value=[mock_port]), \
             patch("elliptec.controller.serial.Serial", return_value=mock_serial):
            ctrl = Controller(port=None, debug=True)
        assert ctrl.port == mock_port  # __connect_to_port receives the port object

    def test_initial_state(self, mock_controller):
        assert mock_controller.last_position is None
        assert mock_controller.last_response is None
        assert mock_controller.last_status is None


class TestControllerContextManager:
    def test_enter_returns_self(self, mock_controller):
        assert mock_controller.__enter__() is mock_controller

    def test_exit_closes_connection(self, mock_controller):
        mock_controller.__exit__(None, None, None)
        mock_controller.s.close.assert_called_once()


class TestControllerReadResponse:
    def test_read_position(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0PO00000064\r\n"
        status = mock_controller.read_response()
        assert status == ("0", "PO", 100)
        assert mock_controller.last_position == 100

    def test_read_status(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0GS00\r\n"
        status = mock_controller.read_response()
        assert status == ("0", "GS", "0")
        # GS does not update last_position
        assert mock_controller.last_position is None

    def test_read_empty(self, mock_controller):
        mock_controller.s.read_until.return_value = b""
        status = mock_controller.read_response()
        assert status is None

    def test_read_info_dict(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0IN0E1234567820230101016800008000\r\n"
        status = mock_controller.read_response()
        assert isinstance(status, dict)
        # dict responses should not update last_position
        assert mock_controller.last_position is None


class TestControllerSendInstruction:
    def test_send_simple(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0GS00\r\n"
        status = mock_controller.send_instruction(b"gs", address="0")
        mock_controller.s.write.assert_called_once_with(b"0gs")
        assert status == ("0", "GS", "0")

    def test_send_with_string_message(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0PO00000064\r\n"
        mock_controller.send_instruction(b"ma", address="0", message="00000064")
        mock_controller.s.write.assert_called_once_with(b"0ma00000064")

    def test_send_with_int_message(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0PO00000064\r\n"
        mock_controller.send_instruction(b"ma", address="0", message=100)
        # 100 = 0x00000064
        mock_controller.s.write.assert_called_once_with(b"0ma00000064")

    def test_send_with_negative_int(self, mock_controller):
        mock_controller.s.read_until.return_value = b"0POFFFFFF9C\r\n"
        mock_controller.send_instruction(b"mr", address="0", message=-100)
        mock_controller.s.write.assert_called_once_with(b"0mrFFFFFF9C")


class TestControllerCloseConnection:
    def test_close_open(self, mock_controller):
        mock_controller.s.is_open = True
        mock_controller.close_connection()
        mock_controller.s.close.assert_called_once()

    def test_close_already_closed(self, mock_controller):
        mock_controller.s.is_open = False
        mock_controller.close_connection()
        mock_controller.s.close.assert_not_called()
