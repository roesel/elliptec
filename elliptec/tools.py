from .errcodes import error_codes

# Basic helper functions

def is_null_or_empty(msg):
        if (not msg.endswith(b'\r\n') or (len(msg) == 0)):
            return True
        else:
            return False

def parse(msg, debug=True):
	if is_null_or_empty(msg):
		if debug:
			print('Parse: Status/Response may be incomplete!')
			print('Parse: Message:', msg)
		return None
	msg = msg.decode().strip()
	code = msg[1:3]
	try: 
		addr_int = int(msg[0], 16)
	except ValueError:
		raise ValueError('Invalid Address: %s' % msg[0])
	addr = msg[0]
	
	if (code.upper() == 'IN'):
		info = {'Address' : addr,
			'Motor Type' : int(msg[3:5], 16),
			'Serial No.' : msg[5:13],
			'Year' : msg[13:17],
			'Firmware' : msg[17:19],
			'Thread' : is_metric(msg[19]),
			'Hardware' : msg[20],
			'Range' : (int(msg[21:25], 16)),
			'Pulse/Rev' : (int(msg[25:], 16)) }
		return info

	elif code.upper() in ['PO', 'BO', 'HO', 'GJ']:
		pos = msg[3:]
		return (addr, code, (s32(int(pos, 16))))

	elif (code.upper() == 'GS'):
		errcode = msg[3:]
		return (addr, code, str(int(errcode, 16)))

	elif (code.upper() in ['I1', 'I2']):
		# Info about motor
		
		# Period=14740000/frequency for backward and forward motor movements 
		# And 1 Amp of current is equal to 1866 points (1 point is 0.54 mA circa)

		info = {
			'Address' : addr,
			'Loop' : msg[3],  # The state of the loop setting (1 = ON, 0 = OFF)
			'Motor' : msg[4], # The state of the motor (1 = ON, 0 = OFF)
			'Current' : int(msg[5:9], 16)/1866, # 1866 points is 1 amp
			'Ramp up' : int(msg[9:13], 16), # PWM increase every ms
			'Ramp down' : int(msg[13:17], 16), # PWM decrease every ms
			'Forward period' : int(msg[17:21], 16), # Forward period value  
			'Backward period' : int(msg[21:25], 16), # Backward period value
			'Forward frequency' : 14740000/int(msg[17:21], 16), # Calculated forward frequency
			'Backward frequency' : 14740000/int(msg[21:25], 16), # Calculated forward frequency
			} 
		return info

	else:
		return (addr, code, msg[3:])

def is_metric(num):
	if (num == '0'):
		thread_type = 'Metric'
	elif(num == '1'):
		thread_type = 'Imperial'
	else:
		thread_type = None

	return thread_type

def int_to_padded_hex(value, padding=8):
	''' Explanation:
			{   	  # Format identifier
			value:    # first parameter
	(not)	#   	  # use "0x" prefix
			0   	  # fill with zeroes
			{padding} # to a length of n characters (including 0x), defined by the second parameter
			X   	  # hexadecimal number, using uppercase letters for a-f
			}   	  # End of format identifier
	'''

	hexadecimal = f"{value:0{padding}X}"
	return hexadecimal

def s32(value): # Convert 32bit signed hex to int
	return -(value & 0x80000000) | (value & 0x7fffffff)

def error_check(status):
	if not status:
		print('Status is None')
	elif isinstance(status, dict):
		print('Status is a dictionary.')
	elif (status[1] == "GS"):
		if (status[2] != '0'): # is there an error?		
			err = error_codes[status[2]]
			print('ERROR: %s' % err)
		else:
			print('Status OK')
	elif (status[1] == "PO"):
		print('Status OK (position)')
	else:
		print('Other status:', status)

def move_check(status):
	if not status:
		print('Status is None')
	elif status[1] == 'GS':
		error_check(status)
	elif ((status[1] == "PO") or (status[1] == "BO")):
		pass
		print('Move Successful.')
	else:
		print('Unknown response code %s' % status[1])