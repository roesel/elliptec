import serial
from .cmd import get_, set_, mov_
from .devices import devices
from .tools import parse, error_check, move_check, int_to_padded_hex
import sys

class Motor():

    def __init__(self, port, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=2, write_timeout=0.5, debug=True):
        try:
            self.s = serial.Serial(port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, write_timeout=write_timeout)
        except serial.SerialException:
            print('Could not open port %s' % port)
            # TODO: nicer/more logical shutdown (this kills the entire app?)
            sys.exit()

        self.last_position = None
        self.debug = debug
        if self.s.is_open:
            if self.debug:
                print('Connection established!')
            self.load_motor_info()
    
    def load_motor_info(self):
        ''' Asks motor for info and load response into properties other methods can check later. '''    
        self.info = self.get('info')
        
        # TODO: Figure out which variables require extracting from info
        self.range = self.info['Range']
        self.pulse_per_rev = self.info['Pulse/Rev']
        self.serial_no = self.info['Serial No.']
        self.motor_type = self.info['Motor Type']
        
    def send_instruction(self, address, instruction, message=None):
        # Encode inputs
        addr = address.encode('utf-8')
        inst = instruction #.encode('utf-8')
        # Compose command
        command = addr + inst
        # Append command if necessary
        if message is not None:
            # Convert to hex if the message is a number
            if isinstance(message, int):
                mesg = int_to_padded_hex(message)
            else:
                mesg = message
            
            command += mesg.encode('utf-8')
        
        # Execute the command and wait for a response
        # TODO: Go through this and try to unify
        self.request = command  # TODO: check if this is necessary
        if self.debug:
            print("TX:", command)
        self.s.write(command) # This actually executes the movement
    
        response = self.read_response()
        
        return response
    
    def read_response(self):
        response = self.s.read_until(b'\r\n') # Waiting until response read
        
        if self.debug:
            print("RX:", response)
        
        status = parse(response) 

        # Setting properties of last response/status/position
        self.last_response = response
        self.last_status = status
        if not isinstance(status, dict):
            if status[0] == 'PO':
                self.last_position = status[1]

        return status
            
    # Action functions
    def move(self, req='home', data='', addr='0'):
        ''' Expects:
            addr - Address of device (0-F)
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
            
        status = self.send_instruction(addr, instruction, message=data)
        if self.debug:
            move_check(status) # This just prints stuff... # TODO: make it return success as boolean?
        return status

    def get(self, req='status', data='', addr='0'):
        # Try to translate command to instruction
        if req in get_:
            instruction = get_[req]
        else:
            print('Invalid Command: %s' % req)
            return None

        status = self.send_instruction(addr, instruction, message=data)
        if self.debug:
            error_check(status) # This just prints stuff... # TODO: make it return success as boolean?

        return status

    def set(self, req='', data='', addr='0'):
        # Try to translate command to instruction
        if req in set_:
            instruction = set_[req]
        else:
            print('Invalid Command: %s' % req)
            return None

        status = self.send_instruction(addr, instruction, message=data)
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

    # TODO: To be implemented
    # set_forward_frequency(self, motor)
    # set_backward_frequency(self, motor)
    # search_frequency(self, motor)
    # save_user_status(self, motor)


    ## Private methods
    def __str__(self):
        string = '\nPort - ' + self.port + '\n\n'
        for key in self.info:
            string += (key + ' - ' + str(self.info[key]) + '\n')            
        return string
