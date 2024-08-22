from src import elliptec

# Test settings (adjust based on hardware)
port = 'COM3'
address = '1'
allowed_error = 0.02

def test_homing():
    '''Test that rotator homes to the home offset set.'''
    # Create objects
    controller = elliptec.Controller(port)
    ro = elliptec.Rotator(controller, address=address)
    
    # Home the rotator to firmware-set position
    ro.home()

    # See if homing moved to home offset set
    reached_angle = ro.get_angle()
    home_offset = ro.get_home_offset()
    # Close the connections for other tests
    controller.close_connection()

    assert abs(reached_angle - home_offset) <= allowed_error, "Reached home location should equal home offset." 

def test_movement():
    '''Test that rotator moves to the desired positions.'''
    # Create objects
    controller = elliptec.Controller(port)
    ro = elliptec.Rotator(controller, address=address)
    
    # Home the rotator before usage
    ro.home()

    # Loop over a list of angles and acquire for each
    for angle in [0, 90, 359]:
        ro.set_angle(angle)
        reached_angle = ro.get_angle()
        assert abs(reached_angle - angle) <= allowed_error, "Reached angle should equal target."
    
    # Close the connection
    controller.close_connection()
