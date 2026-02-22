"""This module contains the Controller class, which is the base class for all devices."""
from __future__ import annotations

import logging
from types import TracebackType

import serial
from .tools import Status, parse

logger = logging.getLogger(__name__)


class Controller:
    """Class for controlling the Elliptec devices via serial port. This is a general class,
    subclasses are implemented for each device type."""

    def __init__(self,
                 port: str | None = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = serial.PARITY_NONE,
                 stopbits: float = serial.STOPBITS_ONE,
                 timeout: float = 2,
                 write_timeout: float = 0.5,
                 debug: bool = True) -> None:
        self.debug = debug
        self.port: str | None = None
        self.last_position: int | str | None = None
        self.last_response: bytes | None = None
        self.last_status: Status | None = None

        if port is None:
            self.__search_and_connect(baudrate,
                                      bytesize,
                                      parity,
                                      stopbits,
                                      timeout,
                                      write_timeout)
        else:
            self.__connect_to_port(port,
                                   baudrate,
                                   bytesize,
                                   parity,
                                   stopbits,
                                   timeout,
                                   write_timeout)

    def __enter__(self) -> Controller:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        self.close_connection()

    def __connect_to_port(self,
                          port: str,
                          baudrate: int,
                          bytesize: int,
                          parity: str,
                          stopbits: float,
                          timeout: float,
                          write_timeout: float) -> None:
        try:
            self.s = serial.Serial(port,
                                   baudrate=baudrate,
                                   bytesize=bytesize,
                                   parity=parity,
                                   stopbits=stopbits,
                                   timeout=timeout,
                                   write_timeout=write_timeout)
        except serial.SerialException:
            logger.error("Could not open port %s", port)
            return

        self.port = port
        if self.s.is_open and self.debug:
            logger.debug("Controller on port %s: Connection established!", port)

    def __search_and_connect(self,
                             baudrate: int,
                             bytesize: int,
                             parity: str,
                             stopbits: float,
                             timeout: float,
                             write_timeout: float) -> None:
        port_list = serial.tools.list_ports.comports()
        for port in port_list:
            self.__connect_to_port(port,
                                   baudrate,
                                   bytesize,
                                   parity,
                                   stopbits,
                                   timeout,
                                   write_timeout)
            break

    def read_response(self) -> Status | None:
        """Reads the response from the controller."""
        response = self.s.read_until(b"\r\n")  # Waiting until response read

        if self.debug:
            logger.debug("RX: %s", response)

        status = parse(response, debug=self.debug)

        # Setting properties of last response/status/position
        self.last_response = response
        self.last_status = status
        if status is not None:
            if not isinstance(status, dict):
                if status[1] == "PO":
                    self.last_position = status[2]

        return status

    def send_instruction(self, instruction: bytes, address: str = "0", message: int | str | None = None) -> Status | None:
        """Sends an instruction to the controller. Expects a response which is returned."""
        # Encode inputs
        addr = address.encode("utf-8")
        inst = instruction  # .encode('utf-8') # Already encoded
        # Compose command
        command = addr + inst
        # Append command if necessary
        if message is not None:
            # Convert to hex if the message is a number
            if isinstance(message, int):
                mesg = message.to_bytes(4, "big", signed=True).hex().upper()
            else:
                mesg = message

            command += mesg.encode("utf-8")

        if self.debug:
            logger.debug("TX: %s", command)
        # Execute the command and wait for a response
        self.s.write(command)  # This actually executes the command
        response = self.read_response()

        return response

    def close_connection(self) -> None:
        """Closes the serial connection."""
        if self.s.is_open:
            self.s.close()
            logger.debug("Connection is closed!")
