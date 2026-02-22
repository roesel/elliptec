"""Module for linear stages. Inherits from elliptec.ContinuousMotor."""
from __future__ import annotations

from .continuous import ContinuousMotor
from .tools import Status


class Linear(ContinuousMotor):
    """Elliptec Linear Motor class."""

    def _pos_to_unit(self, position: int) -> float:
        """Converts position in pulses to distance in millimeters."""
        pulse_range = self.pulse_per_rev * self.range
        return round(position / pulse_range * self.range, 4)

    def _unit_to_pos(self, value: float) -> int:
        """Converts distance in millimeters to position in pulses."""
        pulse_range = self.pulse_per_rev * self.range
        return int(value / self.range * pulse_range)

    # Public API
    def get_distance(self) -> float | None:
        """Finds at which distance the stage is at the moment."""
        return self._get_unit()

    def set_distance(self, distance: float) -> float | None:
        """Moves to a particular distance."""
        return self._set_unit(distance)

    def shift_distance(self, distance: float) -> float | None:
        """Shifts by a particular distance."""
        return self._shift_unit(distance)

    # Backward compatibility aliases
    def extract_distance_from_status(self, status: Status | None) -> float | None:
        """Extracts distance from status."""
        return self._extract_unit_from_status(status)

    def pos_to_dist(self, position: int) -> float:
        """Converts position in pulses to distance in millimeters."""
        return self._pos_to_unit(position)

    def dist_to_pos(self, distance: float) -> int:
        """Converts distance in millimeters to position in pulses."""
        return self._unit_to_pos(distance)
