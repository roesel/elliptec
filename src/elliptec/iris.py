"""Module for linear stages. Inherits from elliptec.Motor."""
from . import Motor
from .devices import devices

class Iris(Motor):
    """Iris class for elliptec motorized iris. Inherits from elliptec.Motor."""

    def __init__(self, controller, address="0", debug=True):
        # Patch parent object - elliptec.Motor(port, baud, bytesize, parity)
        super().__init__(controller=controller, address=address, debug=debug)
    
    
    def check_move(self, target_aperture):
        min_aperture = devices[self.motor_type]["min_aperture"]
        max_aperture = devices[self.motor_type]["max_aperture"]
        return target_aperture >= min_aperture and target_aperture <= max_aperture

    ## Setting and getting positions
    def get_aperture(self):
        """Finds at which aperture the iris is at the moment."""
        status = self.get("position")
        aperture = self.extract_aperture_from_status(status)
        return aperture

    def set_aperture(self, aperture):
        """Moves to a particular aperture."""
        if self.check_move(aperture):
            position = self.dist_to_pos(aperture)
            status = self.move("absolute", (position))
            aperture = self.extract_aperture_from_status(status)
            return aperture
        else:
            return None
        

    def shift_aperture(self, distance):
        """Shifts by a particular amount."""
        current_aperture = self.get_aperture()
        target_aperture = current_aperture + distance
        if self.check_move(target_aperture):
            position = self.dist_to_pos(distance)
            status = self.move("relative", position)
            aperture = self.extract_aperture_from_status(status)
            return aperture
        else:
            return None

    def jog(self, direction="forward"):
        """Jogs by the jog amount in a particular direction."""
        if direction in ["backward", "forward"]:
            status = self.move(direction)
            position = self.extract_aperture_from_status(status)
            return position
        else:
            return None

    # Home set/get
    def get_home_offset(self):
        """Gets the home offset."""
        status = self.get("home_offset")
        aperture = self.extract_aperture_from_status(status)
        return aperture

    def set_home_offset(self, offset):
        """Sets the home offset."""
        position = self.dist_to_pos(offset)
        status = self.set("home_offset", position)
        return status

    # Jog step
    def get_jog_step(self):
        """Gets the jog step."""
        status = self.get("stepsize")
        aperture = self.extract_aperture_from_status(status)
        return aperture

    def set_jog_step(self, aperture):
        """Sets jog step to a particular aperture (in millimeters)."""
        position = self.dist_to_pos(aperture)
        status = self.set("stepsize", position)
        return status

    # TODO: clean(self)
    # TODO: clean_and_optimize(self)

    # Helper functions
    def extract_aperture_from_status(self, status):
        """Extracts aperture from status."""
        # If status is telling us current position
        if status:
            if status[1] in ["PO", "HO", "GJ"]:
                position = status[2]
                aperture = self.pos_to_dist(position)
                return aperture

        return None

    def pos_to_dist(self, position):
        """Converts position in pulses to aperture in millimeters."""
        pulse_range = self.pulse_per_rev * self.range
        aperture = position / pulse_range * self.range
        aperture_rounded = round(aperture, 4)
        return aperture_rounded

    def dist_to_pos(self, aperture):
        """Converts aperture in millimeters to position in pulses."""
        pulse_range = self.pulse_per_rev * self.range
        position = int(aperture / self.range * pulse_range)
        return position
