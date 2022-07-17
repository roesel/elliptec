from .cmd import get_, set_, mov_
from .tools import error_check, move_check
from .errors import ExternalDeviceNotFound

class Motor():

    def __init__(self, controller, address='0', debug=True):
        
        # the controller object which services the COM port
        self.controller = controller
        # self.address is kept as a 0-F string and encoded in send_instruction()
        self.address = address
        self.debug = debug
        
        self.last_position = None

        # Load motor info on creation
        self.load_motor_info()
    
    def load_motor_info(self):
        ''' Asks motor for info and load response into properties other methods can check later. '''    
        info = self.get('info')
        if info is None:
            raise ExternalDeviceNotFound
        else:
            self.info = info
        
            # TODO: Figure out which variables require extracting from info
            self.range = self.info['Range']
            self.pulse_per_rev = self.info['Pulse/Rev']
            self.serial_no = self.info['Serial No.']
            self.motor_type = self.info['Motor Type']
        
    def send_instruction(self, instruction, message=None):
        response = self.controller.send_instruction(
            instruction, 
            address=self.address, 
            message=message
        )

        return response

    # Action functions
    def move(self, req='home', data=''):
        ''' Expects:
            req - Name of request
            data - Parameters to be sent after address and request
        '''
        # Try to translate command to instruction
        if req in mov_:
            instruction = mov_[req]
        else:
            print('Invalid Command: %s' % req)
            return False

        # Add '0' to end of 'home' instruction
        # I don't want to do it systematically, since at least fw and bw don't have it
        if instruction == b'ho':
            instruction = b'ho0'
            
        status = self.send_instruction(instruction, message=data)
        if self.debug:
            move_check(status) # This just prints stuff... # TODO: make it return success as boolean?
        return status

    def get(self, req='status', data=''):
        # Try to translate command to instruction
        if req in get_:
            instruction = get_[req]
        else:
            print('Invalid Command: %s' % req)
            return None

        status = self.send_instruction(instruction, message=data)
        if self.debug:
            error_check(status) # This just prints stuff... # TODO: make it return success as boolean?

        return status

    def set(self, req='', data=''):
        # Try to translate command to instruction
        if req in set_:
            instruction = set_[req]
        else:
            print('Invalid Command: %s' % req)
            return None

        status = self.send_instruction(instruction, message=data)
        if self.debug:
            error_check(status) # This just prints stuff... # TODO: make it return success as boolean?

        return status

    # Wrapper functions
    def home(self, clockwise="True"):
        ''' Wrapper function to easily enable access to homing.'''
        if clockwise:
            self.move('home_clockwise')
        else:
            self.move('home_anticlockwise')

    def change_address(self, new_address):
        old_address = self.address
        status = self.set('address', data=new_address)
        if status[0] == new_address:
            # Make the Motor object know about the change
            self.address = new_address  
            if self.debug:
                print('Address successfully changed from {} to {}.'.format(old_address, new_address))

    # TODO: To be implemented
    # set_forward_frequency(self, motor)
    # set_backward_frequency(self, motor)
    # search_frequency(self, motor)
    # save_user_status(self, motor)


    ## Private methods
    def __str__(self):
        string = ''
        for key in self.info:
            string += (key + ' - ' + str(self.info[key]) + '\n')            
        return string
    
    def close(self):
        self.controller.close()
