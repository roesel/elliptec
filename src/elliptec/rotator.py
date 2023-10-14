"""Module for rotation mount (ELL14) or rotary stage (ELL18). Inherits from elliptec.Motor."""
from . import Motor


class Rotator(Motor):
    """Class for rotation mounts such as a rotating mount (ELL14) or rotary stage (ELL18)."""

    # TODO: Merge this class with Linear() via common ancestor

    def __init__(self, controller, address="0", debug=True):
        # Patch parent object - elliptec.Motor(port, baud, bytesize, parity)
        super().__init__(controller=controller, address=address, debug=debug)

    ## Position control
    def get_angle(self):
        """Finds at which angle (in degrees) the rotator is at the moment."""
        status = self.get("position")
        angle = self.extract_angle_from_status(status)
        return angle

    def set_angle(self, angle):
        """Moves the rotator to a particular angle (in degrees)."""
        position = self.angle_to_pos(angle)
        status = self.move("absolute", position)
        angle = self.extract_angle_from_status(status)
        return angle

    def shift_angle(self, angle):
        """Shifts by a particular angle (in degrees)."""
        position = self.angle_to_pos(angle)
        status = self.move("relative", position)
        angle = self.extract_angle_from_status(status)
        return angle

    def jog(self, direction="forward"):
        """Jogs by the jog distance in a particular direction."""
        if direction in ["backward", "forward"]:
            status = self.move(direction)
            angle = self.extract_angle_from_status(status)
            return angle
        else:
            return None

    # Home set/get
    def get_home_offset(self):
        """Gets the home offset."""
        status = self.get("home_offset")
        angle = self.extract_angle_from_status(status)
        return angle

    def set_home_offset(self, offset):
        """Sets the home offset."""
        position = self.angle_to_pos(offset)
        status = self.set("home_offset", position)
        return status

    # Jog step
    def get_jog_step(self):
        """Gets the jog step."""
        status = self.get("stepsize")
        angle = self.extract_angle_from_status(status)
        return angle

    def set_jog_step(self, angle):
        """Sets jog step to a particular angle (in degrees)."""
        position = self.angle_to_pos(angle)
        status = self.set("stepsize", position)
        return status

    # TODO: clean(self)
    # TODO: clean_and_optimize(self)

    # Helper functions
    def extract_angle_from_status(self, status):
        """Extracts angle from status."""
        # If status is telling us current position
        if status:
            if status[1] in ["PO", "HO", "GJ"]:
                position = int(status[2])
                angle = self.pos_to_angle(position)
                return angle

        return None

    def pos_to_angle(self, posval):
        """Converts position in pulses to angle in degrees."""
        angle = posval / self.pulse_per_rev * self.range
        angle_rounded = round(angle, 4)
        return angle_rounded

    def angle_to_pos(self, angleval):
        """Converts angle in degrees to position in pulses."""
        position = int(angleval / self.range * self.pulse_per_rev)
        return position
