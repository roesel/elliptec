"""A module that contains the Motor class, which is the base class for all motors."""
from __future__ import annotations

import logging
from abc import ABC
from collections.abc import Callable

from .cmd import get_, set_, mov_, do_
from .controller import Controller
from .tools import Status, error_check, move_check
from .errors import ExternalDeviceNotFound

logger = logging.getLogger(__name__)


class Motor(ABC):
    """A class that represents a general motor. Each device inherits from this class."""

    def __init__(self, controller: Controller, address: str = "0", debug: bool = True) -> None:
        # the controller object which services the COM port
        self.controller = controller
        # self.address is kept as a 0-F string and encoded in send_instruction()
        self.address = address
        self.debug = debug

        self.last_position: int | str | None = None

        # Load motor info on creation
        self.load_motor_info()

    def load_motor_info(self) -> None:
        """Asks motor for info and load response into properties other methods can check later."""
        info = self.get("info")
        if info is None:
            raise ExternalDeviceNotFound
        else:
            self.info = info

            # TODO: Figure out which variables require extracting from info
            self.range = self.info["Range"]
            self.pulse_per_rev = self.info["Pulse/Rev"]
            self.serial_no = self.info["Serial No."]
            self.motor_type = self.info["Motor Type"]

    def send_instruction(self, instruction: bytes, message: int | str | None = None) -> Status | None:
        """Sends an instruction to the motor. Returns the response from the motor."""
        response = self.controller.send_instruction(instruction, address=self.address, message=message)

        return response

    # Action functions
    def _execute(self, command_dict: dict[str, bytes], req: str, data: int | str | None = None, check_fn: Callable[[Status | None], None] = error_check) -> Status | None:
        """Looks up and executes a command from the given dictionary."""
        if req not in command_dict:
            logger.error("Invalid Command: %s", req)
            return None
        status = self.send_instruction(command_dict[req], message=data)
        if self.debug:
            check_fn(status)
        return status

    def move(self, req: str = "home", data: int | str = "") -> Status | None | bool:
        """Wrapper function to easily enable access to movement.
        Expects:
        req - Name of request
        data - Parameters to be sent after address and request
        """
        # Try to translate command to instruction
        if req not in mov_:
            logger.error("Invalid Command: %s", req)
            return False

        instruction = mov_[req]

        # Add '0' to end of 'home' instruction
        # I don't want to do it systematically, since at least fw and bw don't have it
        if instruction == b"ho":
            instruction = b"ho0"

        status = self.send_instruction(instruction, message=data)
        if self.debug:
            move_check(status)
        return status

    def get(self, req: str = "status", data: int | str = "") -> Status | None:
        """Generates get instructions from commands."""
        return self._execute(get_, req, data=data)

    def set(self, req: str = "", data: int | str = "") -> Status | None:
        """Generates set instructions from commands."""
        return self._execute(set_, req, data=data)

    def do(self, req: str = "") -> Status | None:
        """Generates do instructions from commands."""
        return self._execute(do_, req)

    # Wrapper functions
    def home(self, clockwise: bool = True) -> Status | None | bool:
        """Wrapper function to easily enable access to homing."""
        if clockwise:
            return self.move("home_clockwise")
        else:
            return self.move("home_anticlockwise")

    def change_address(self, new_address: str) -> None:
        """Changes the address of the motor."""
        old_address = self.address
        status = self.set("address", data=new_address)
        if status[0] == new_address:
            # Make the Motor object know about the change
            self.address = new_address
            if self.debug:
                logger.debug("Address successfully changed from %s to %s.", old_address, new_address)

    def save_user_data(self) -> None:
        """Saves the user data to the motor."""
        self.do("save_user_data")

    # TODO: To be implemented
    # set_forward_frequency(self, motor)
    # set_backward_frequency(self, motor)
    # search_frequency(self, motor)
    # save_user_status(self, motor)

    ## Private methods
    def __str__(self) -> str:
        """Returns a string representation of the motor."""
        return "".join(f"{key} - {self.info[key]}\n" for key in self.info)

    def close_connection(self) -> None:
        """Closes the serial port."""
        self.controller.close_connection()
