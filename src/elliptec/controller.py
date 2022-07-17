import serial
from .tools import parse, int_to_padded_hex
import sys

class Controller():

    def __init__(self, port, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=2, write_timeout=0.5, debug=True):
        try:
            self.s = serial.Serial(port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, write_timeout=write_timeout)
        except serial.SerialException:
            print('Could not open port %s' % port)
            # TODO: nicer/more logical shutdown (this kills the entire app?)
            sys.exit()

        self.debug = debug
        self.port = port

        if self.s.is_open:
            if self.debug:
                print('Controller on port {}: Connection established!'.format(port))

    def read_response(self):
        response = self.s.read_until(b'\r\n') # Waiting until response read
        
        if self.debug:
            print("RX:", response)
        
        status = parse(response, debug=self.debug) 

        # Setting properties of last response/status/position
        self.last_response = response
        self.last_status = status
        #print('STATUS:', status)
        if status is not None:
            if not isinstance(status, dict):
                if status[1] == 'PO':
                    self.last_position = status[1]

        return status

    def send_instruction(self, instruction, address='0', message=None):
        # Encode inputs
        addr = address.encode('utf-8')
        inst = instruction #.encode('utf-8') # Already encoded
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
        
        if self.debug:
            print("TX:", command)
        # Execute the command and wait for a response 
        self.s.write(command) # This actually executes the command
        response = self.read_response()
        
        return response
    
    def close(self):
        if self.s.is_open:
            self.s.close()
            print("Connection is closed!")

    