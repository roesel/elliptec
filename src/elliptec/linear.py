"""Module for linear stages. Inherits from elliptec.Motor."""
from . import Motor


class Linear(Motor):
    """Elliptec Linear Motor class. Inherits from elliptec.Motor."""

    def __init__(self, controller, address="0", debug=True):
        # Patch parent object - elliptec.Motor(port, baud, bytesize, parity)
        super().__init__(controller=controller, address=address, debug=debug)

    ## Setting and getting positions
    def get_distance(self):
        """Finds at which distance the stage is at the moment."""
        status = self.get("position")
        distance = self.extract_distance_from_status(status)
        return distance

    def set_distance(self, distance):
        """Moves to a particular distance."""
        position = self.dist_to_pos(distance)
        status = self.move("absolute", (position))
        distance = self.extract_distance_from_status(status)
        return distance

    def shift_distance(self, distance):
        """Shifts by a particular distance."""
        position = self.dist_to_pos(distance)
        status = self.move("relative", position)
        distance = self.extract_distance_from_status(status)
        return distance

    def jog(self, direction="forward"):
        """Jogs by the jog distance in a particular direction."""
        if direction in ["backward", "forward"]:
            status = self.move(direction)
            position = self.extract_distance_from_status(status)
            return position
        else:
            return None

    # Home set/get
    def get_home_offset(self):
        """Gets the home offset."""
        status = self.get("home_offset")
        distance = self.extract_distance_from_status(status)
        return distance

    def set_home_offset(self, offset):
        """Sets the home offset."""
        position = self.dist_to_pos(offset)
        status = self.set("home_offset", position)
        return status

    # Jog step
    def get_jog_step(self):
        """Gets the jog step."""
        status = self.get("stepsize")
        distance = self.extract_distance_from_status(status)
        return distance

    def set_jog_step(self, distance):
        """Sets jog step to a particular distance (in millimeters)."""
        position = self.dist_to_pos(distance)
        status = self.set("stepsize", position)
        return status

    # TODO: clean(self)
    # TODO: clean_and_optimize(self)

    # Helper functions
    def extract_distance_from_status(self, status):
        """Extracts distance from status."""
        # If status is telling us current position
        if status:
            if status[1] in ["PO", "HO", "GJ"]:
                position = status[2]
                distance = self.pos_to_dist(position)
                return distance

        return None

    def pos_to_dist(self, position):
        """Converts position in pulses to distance in millimeters."""
        pulse_range = self.pulse_per_rev * self.range
        distance = position / pulse_range * self.range
        distance_rounded = round(distance, 4)
        return distance_rounded

    def dist_to_pos(self, distance):
        """Converts distance in millimeters to position in pulses."""
        pulse_range = self.pulse_per_rev * self.range
        position = int(distance / self.range * pulse_range)
        return position
