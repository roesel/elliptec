"""Base class for continuous-position motors (rotators, linear stages, irises)."""
from __future__ import annotations

from abc import abstractmethod

from .motor import Motor
from .tools import Status


class ContinuousMotor(Motor):
    """Base class for motors that move to continuous positions (as opposed to discrete slots).

    Subclasses must implement:
        _pos_to_unit(position) -> float: Convert pulse position to user unit
        _unit_to_pos(value) -> int: Convert user unit to pulse position
    """

    @abstractmethod
    def _pos_to_unit(self, position: int) -> float:
        ...

    @abstractmethod
    def _unit_to_pos(self, value: float) -> int:
        ...

    def _get_unit(self) -> float | None:
        """Gets the current position in user units."""
        status = self.get("position")
        return self._extract_unit_from_status(status)

    def _set_unit(self, value: float) -> float | None:
        """Moves to an absolute position in user units."""
        position = self._unit_to_pos(value)
        status = self.move("absolute", position)
        return self._extract_unit_from_status(status)

    def _shift_unit(self, value: float) -> float | None:
        """Shifts by a relative amount in user units."""
        position = self._unit_to_pos(value)
        status = self.move("relative", position)
        return self._extract_unit_from_status(status)

    def jog(self, direction: str = "forward") -> float | None:
        """Jogs by the jog distance in a particular direction."""
        if direction in ["backward", "forward"]:
            status = self.move(direction)
            return self._extract_unit_from_status(status)
        return None

    def get_home_offset(self) -> float | None:
        """Gets the home offset."""
        status = self.get("home_offset")
        return self._extract_unit_from_status(status)

    def set_home_offset(self, offset: float) -> Status | None:
        """Sets the home offset."""
        position = self._unit_to_pos(offset)
        return self.set("home_offset", position)

    def get_jog_step(self) -> float | None:
        """Gets the jog step."""
        status = self.get("stepsize")
        return self._extract_unit_from_status(status)

    def set_jog_step(self, value: float) -> Status | None:
        """Sets the jog step size."""
        position = self._unit_to_pos(value)
        return self.set("stepsize", position)

    def _extract_unit_from_status(self, status: Status | None) -> float | None:
        """Extracts user-unit value from a status tuple."""
        if status and status[1] in ["PO", "HO", "GJ"]:
            return self._pos_to_unit(int(status[2]))
        return None
