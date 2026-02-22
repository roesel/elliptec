"""Module for shutter. Inherits from elliptec.Motor."""
from __future__ import annotations

from .controller import Controller
from .devices import devices
from .tools import Status
from . import Motor


class Shutter(Motor):
    """Class for shutter objects, typically two-position linear sliders. Inherits from elliptec.Motor."""

    def __init__(self, controller: Controller, address: str = "0", debug: bool = True, inverted: bool = False) -> None:
        super().__init__(controller=controller, address=address, debug=debug)
        self.inverted = inverted

    # Functions specific to Shutter

    ## Setting and getting slots for Slider approach
    def get_slot(self) -> int | None:
        """Finds at which slot the slider is at the moment."""
        status = self.get("position")
        slot = self.extract_slot_from_status(status)
        return slot

    def set_slot(self, slot: int) -> int | None:
        """Moves the slider to a particular slot."""
        # If the slider is elsewhere, move it.
        if slot == 1:
            status = self.move("backward")
            slot = self.extract_slot_from_status(status)
            return slot
        elif slot == 2:
            status = self.move("forward")
            slot = self.extract_slot_from_status(status)
            return slot
        else:
            return None

    def jog(self, direction: str = "forward") -> int | None:
        """Jogs by the jog distance in a particular direction."""
        if direction in ["backward", "forward"]:
            status = self.move(direction)
            slot = self.extract_slot_from_status(status)
            return slot
        else:
            return None

    ## Opening and closing for Shutter approach
    def open(self) -> int | None:
        """Opens the shutter. Actual position depends on whether or not inverted=True is
        passed to the shutter at creation.
        """
        return self.set_slot(1 if self.inverted else 2)

    def close(self) -> int | None:
        """Closes the shutter. Actual position depends on whether or not inverted=True is
        passed to the shutter at creation.
        """
        return self.set_slot(2 if self.inverted else 1)

    def is_open(self) -> bool:
        """Returns True if shutter is open, False if closed."""
        return self.get_slot() == (1 if self.inverted else 2)

    def is_closed(self) -> bool:
        """Returns True if shutter is closed, False if open."""
        return self.get_slot() == (2 if self.inverted else 1)

    # Helper functions
    def extract_slot_from_status(self, status: Status | None) -> int | None:
        """Extracts slot from status."""
        # If status is telling us current position
        if status:
            if status[1] == "PO":
                position = status[2]
                slot = self.pos_to_slot(position)
                return slot

        return None

    def pos_to_slot(self, posval: int) -> int:
        """Converts position value to slot number."""
        slots = devices[self.motor_type]["slots"]
        factor = self.range / (slots - 1)
        slot = int(posval / factor) + 1
        return slot

    def slot_to_pos(self, slot: int) -> int:
        """Converts slot number to position value."""
        slots = devices[self.motor_type]["slots"]
        factor = self.range / (slots - 1)
        position = int((slot - 1) * factor)
        return position
