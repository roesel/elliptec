from .devices import devices
from . import Motor

class Shutter(Motor):

    def __init__(self, controller, address='0', debug=True, inverted=False):
        # Patch parent object - elliptec.Motor(port, baud, bytesize, parity)
        super().__init__(controller=controller, address=address, debug=debug)
        self.inverted = inverted
    
    # Functions specific to Shutter

    ## Setting and getting slots for Slider approach
    def get_slot(self):
        ''' Finds at which slot the slider is at the moment. '''
        status = self.get('position')
        slot = self.extract_slot_from_status(status)
        return slot
        
    
    def set_slot(self, slot):
        ''' Moves the slider to a particular slot. 
        '''
        # If the slider is elsewhere, move it.
        if (slot == 1):
            status = self.move('backward')
            slot = self.extract_slot_from_status(status)
            return slot
        elif (slot == 2):
            status = self.move('forward')
            slot = self.extract_slot_from_status(status)
            return slot
        else:
            return None

    def jog(self, direction="forward"):
        if direction in ["backward", "forward"]:
            status = self.move(direction)
            slot = self.extract_slot_from_status(status)
            return slot
        else:
            return None

    ## Opening and closing for Shutter approach
    def open(self):
        ''' Opens the shutter. Actual position depends on whether or not inverted=True is 
            passed to the shutter at creation.  
        '''
        if not self.inverted:
            return self.set_slot(2)
        else:
            return self.set_slot(1)
    
    def close(self):
        ''' Closes the shutter. Actual position depends on whether or not inverted=True is 
            passed to the shutter at creation.
        '''
        if not self.inverted:
            return self.set_slot(1)
        else:
            return self.set_slot(2)

    def is_open(self):
        if not self.inverted:
            return (self.get_slot() == 2)
        else:
            return (self.get_slot() == 1)

    def is_closed(self):
        if not self.inverted:
            return (self.get_slot() == 1)
        else:
            return (self.get_slot() == 2)

    # Helper functions
    def extract_slot_from_status(self, status):
        # If status is telling us current position
        if status:
            if status[1]=='PO':
                position = status[2]
                slot = self.pos_to_slot(position)
                return slot
        
        return None

    def pos_to_slot(self, posval):
        slots = devices[self.motor_type]['slots']
        factor = self.range / (slots - 1)
        slot = int(posval/factor) + 1
        return slot
    
    def slot_to_pos(self, slot):
        slots = devices[self.motor_type]['slots']
        factor = self.range / (slots - 1)
        position = int((slot - 1)*factor)
        return position


    



    










