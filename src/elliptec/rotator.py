"""Module for rotation mount (ELL14) or rotary stage (ELL18). Inherits from elliptec.ContinuousMotor."""
from .continuous import ContinuousMotor


class Rotator(ContinuousMotor):
    """Class for rotation mounts such as a rotating mount (ELL14) or rotary stage (ELL18)."""

    def _pos_to_unit(self, position):
        """Converts position in pulses to angle in degrees."""
        return round(position / self.pulse_per_rev * self.range, 4)

    def _unit_to_pos(self, value):
        """Converts angle in degrees to position in pulses."""
        return int(value / self.range * self.pulse_per_rev)

    # Public API
    def get_angle(self):
        """Finds at which angle (in degrees) the rotator is at the moment."""
        return self._get_unit()

    def set_angle(self, angle):
        """Moves the rotator to a particular angle (in degrees)."""
        return self._set_unit(angle)

    def shift_angle(self, angle):
        """Shifts by a particular angle (in degrees)."""
        return self._shift_unit(angle)

    # Backward compatibility aliases
    def extract_angle_from_status(self, status):
        """Extracts angle from status."""
        return self._extract_unit_from_status(status)

    def pos_to_angle(self, posval):
        """Converts position in pulses to angle in degrees."""
        return self._pos_to_unit(posval)

    def angle_to_pos(self, angleval):
        """Converts angle in degrees to position in pulses."""
        return self._unit_to_pos(angleval)
