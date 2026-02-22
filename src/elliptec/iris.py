"""Module for motorized iris (ELL15). Inherits from elliptec.ContinuousMotor."""
from __future__ import annotations

from .continuous import ContinuousMotor
from .devices import devices
from .tools import Status


class Iris(ContinuousMotor):
    """Iris class for elliptec motorized iris."""

    def check_move(self, target_aperture: float) -> bool:
        min_aperture = devices[self.motor_type]["min_aperture"]
        max_aperture = devices[self.motor_type]["max_aperture"]
        return min_aperture <= target_aperture <= max_aperture

    def _pos_to_unit(self, position: int) -> float:
        """Converts position in pulses to aperture in millimeters."""
        pulse_range = self.pulse_per_rev * self.range
        return round(position / pulse_range * self.range, 4)

    def _unit_to_pos(self, value: float) -> int:
        """Converts aperture in millimeters to position in pulses."""
        pulse_range = self.pulse_per_rev * self.range
        return int(value / self.range * pulse_range)

    # Public API (with bounds checking)
    def get_aperture(self) -> float | None:
        """Finds at which aperture the iris is at the moment."""
        return self._get_unit()

    def set_aperture(self, aperture: float) -> float | None:
        """Moves to a particular aperture."""
        if self.check_move(aperture):
            return self._set_unit(aperture)
        return None

    def shift_aperture(self, distance: float) -> float | None:
        """Shifts by a particular amount."""
        current_aperture = self.get_aperture()
        target_aperture = current_aperture + distance
        if self.check_move(target_aperture):
            return self._shift_unit(distance)
        return None

    # Backward compatibility aliases
    def extract_aperture_from_status(self, status: Status | None) -> float | None:
        """Extracts aperture from status."""
        return self._extract_unit_from_status(status)

    def pos_to_dist(self, position: int) -> float:
        """Converts position in pulses to aperture in millimeters."""
        return self._pos_to_unit(position)

    def dist_to_pos(self, aperture: float) -> int:
        """Converts aperture in millimeters to position in pulses."""
        return self._unit_to_pos(aperture)
