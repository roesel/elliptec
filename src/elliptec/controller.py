"""This module contains the Controller class, which is the base class for all devices."""

import serial
from .tools import parse


class Controller:
    """Class for controlling the Elliptec devices via serial port. This is a general class,
    subclasses are implemented for each device type."""

    last_position = None
    last_response = None
    last_status = None

    def __init__(self, 
                 port = None, 
                 baudrate=9600, 
                 bytesize=8, 
                 parity=serial.PARITY_NONE, 
                 stopbits=serial.STOPBITS_ONE, 
                 timeout=2, 
                 write_timeout=0.5, 
                 debug=True):
        self.debug = debug
        if port is None: 
            self.__search_and_connect(baudrate, 
                                      bytesize, 
                                      parity, 
                                      stopbits, 
                                      timeout, 
                                      write_timeout)
        else: 
            self.__connect_to_port(port, 
                                   baudrate, 
                                   bytesize, 
                                   parity, 
                                   stopbits, 
                                   timeout, 
                                   write_timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def __connect_to_port(self, 
                          port, 
                          baudrate, 
                          bytesize, 
                          parity, 
                          stopbits, 
                          timeout, 
                          write_timeout):
        try:
            self.s = serial.Serial(port, 
                                   baudrate=baudrate, 
                                   bytesize=bytesize, 
                                   parity=parity, 
                                   stopbits=stopbits, 
                                   timeout=timeout, 
                                   write_timeout=write_timeout)
            
        except serial.SerialException:
            print('Could not open port %s' % port)
            self.s.close()
            
        if self.s.is_open:
            if self.debug:
                print('Controller on port {}: Connection established!'.format(port))
        
    def __search_and_connect(self, 
                             baudrate, 
                             bytesize, 
                             parity, 
                             stopbits, 
                             timeout, 
                             write_timeout):
        port_list = serial.tools.list_ports.comports()
        for port in port_list:
            self.__connect_to_port(port, 
                                   baudrate, 
                                   bytesize, 
                                   parity, 
                                   stopbits, 
                                   timeout, 
                                   write_timeout)
            break

    def read_response(self):
        """Reads the response from the controller."""
        response = self.s.read_until(b"\r\n")  # Waiting until response read

        if self.debug:
            print("RX:", response)

        status = parse(response, debug=self.debug)

        # Setting properties of last response/status/position
        self.last_response = response
        self.last_status = status
        # print('STATUS:', status)
        if status is not None:
            if not isinstance(status, dict):
                if status[1] == "PO":
                    self.last_position = status[1]

        return status

    def send_instruction(self, instruction, address="0", message=None):
        """Sends an instruction to the controller. Expects a response which is returned."""
        # Encode inputs
        addr = address.encode("utf-8")
        inst = instruction  # .encode('utf-8') # Already encoded
        # Compose command
        command = addr + inst
        # Append command if necessary
        if message is not None:
            # Convert to hex if the message is a number
            if isinstance(message, int):
                mesg = message.to_bytes(4, "big", signed=True).hex().upper()
            else:
                mesg = message

            command += mesg.encode("utf-8")

        if self.debug:
            print("TX:", command)
        # Execute the command and wait for a response
        self.s.write(command)  # This actually executes the command
        response = self.read_response()

        return response

    def close_connection(self):
        """Closes the serial connection."""
        if self.s.is_open:
            self.s.close()
            print("Connection is closed!")
