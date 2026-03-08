"""Tests for device classes using mocked Controller — no hardware needed.

Strategy: mock Controller.send_instruction to return canned protocol responses.
Motor.__init__ calls load_motor_info() which calls get("info"), so we make
send_instruction return a valid info dict on the first call, then swap to
return position/status tuples for subsequent calls.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from conftest import make_info_response


# ---------------------------------------------------------------------------
# Helper to build a device instance without real hardware
# ---------------------------------------------------------------------------

def _make_device(cls, motor_type: int, pulse_per_rev: int, range_: int, **extra_init):
    """Instantiate a device class with a mocked controller.

    The first send_instruction call (from load_motor_info) returns a canned
    info dict.  After that, send_instruction returns whatever we configure
    via device.controller.send_instruction.return_value.
    """
    info = make_info_response(motor_type=motor_type, pulse_per_rev=pulse_per_rev, range_=range_)

    mock_ctrl = MagicMock()
    mock_ctrl.send_instruction.return_value = info

    device = cls(controller=mock_ctrl, address="0", debug=True, **extra_init)

    # Verify info was loaded
    assert device.motor_type == motor_type
    assert device.pulse_per_rev == pulse_per_rev
    assert device.range == range_

    return device


# ===========================================================================
# Rotator (ELL14 / ELL18)
# ===========================================================================

class TestRotator:
    @pytest.fixture
    def rotator(self):
        from elliptec.rotator import Rotator
        return _make_device(Rotator, motor_type=14, pulse_per_rev=32768, range_=360)

    # -- Pure conversion (no mocking needed beyond init) --
    def test_pos_to_angle_zero(self, rotator):
        assert rotator._pos_to_unit(0) == 0.0

    def test_pos_to_angle_full(self, rotator):
        assert rotator._pos_to_unit(32768) == 360.0

    def test_pos_to_angle_half(self, rotator):
        assert rotator._pos_to_unit(16384) == 180.0

    def test_angle_to_pos(self, rotator):
        assert rotator._unit_to_pos(180.0) == 16384

    def test_angle_to_pos_zero(self, rotator):
        assert rotator._unit_to_pos(0.0) == 0

    def test_backward_compat_aliases(self, rotator):
        assert rotator.pos_to_angle(32768) == 360.0
        assert rotator.angle_to_pos(360.0) == 32768

    # -- Higher-level methods (mock send_instruction to return PO) --
    def test_get_angle(self, rotator):
        rotator.controller.send_instruction.return_value = ("0", "PO", 16384)
        angle = rotator.get_angle()
        assert angle == 180.0

    def test_set_angle(self, rotator):
        rotator.controller.send_instruction.return_value = ("0", "PO", 16384)
        angle = rotator.set_angle(180.0)
        assert angle == 180.0

    def test_shift_angle(self, rotator):
        rotator.controller.send_instruction.return_value = ("0", "PO", 8192)
        angle = rotator.shift_angle(90.0)
        assert angle == 90.0

    def test_extract_angle_from_status(self, rotator):
        assert rotator.extract_angle_from_status(("0", "PO", 32768)) == 360.0
        assert rotator.extract_angle_from_status(None) is None


# ===========================================================================
# Linear (ELL20)
# ===========================================================================

class TestLinear:
    @pytest.fixture
    def linear(self):
        from elliptec.linear import Linear
        # ELL20: 60mm range, pulse_per_rev typically large
        return _make_device(Linear, motor_type=20, pulse_per_rev=32768, range_=60)

    def test_pos_to_dist_zero(self, linear):
        assert linear._pos_to_unit(0) == 0.0

    def test_pos_to_dist(self, linear):
        # pulse_range = 32768 * 60 = 1966080
        # dist = position / pulse_range * range
        pulse_range = 32768 * 60
        pos = pulse_range  # full range
        assert linear._pos_to_unit(pos) == 60.0

    def test_dist_to_pos(self, linear):
        pulse_range = 32768 * 60
        assert linear._unit_to_pos(60.0) == pulse_range

    def test_backward_compat_aliases(self, linear):
        assert linear.pos_to_dist(0) == 0.0
        assert linear.dist_to_pos(0.0) == 0

    def test_get_distance(self, linear):
        linear.controller.send_instruction.return_value = ("0", "PO", 0)
        assert linear.get_distance() == 0.0

    def test_set_distance(self, linear):
        linear.controller.send_instruction.return_value = ("0", "PO", 0)
        assert linear.set_distance(0.0) == 0.0

    def test_shift_distance(self, linear):
        linear.controller.send_instruction.return_value = ("0", "PO", 0)
        assert linear.shift_distance(0.0) == 0.0

    def test_extract_distance_from_status(self, linear):
        assert linear.extract_distance_from_status(("0", "PO", 0)) == 0.0
        assert linear.extract_distance_from_status(None) is None


# ===========================================================================
# Iris (ELL15)
# ===========================================================================

class TestIris:
    @pytest.fixture
    def iris(self):
        from elliptec.iris import Iris
        return _make_device(Iris, motor_type=15, pulse_per_rev=32768, range_=12)

    def test_check_move_in_range(self, iris):
        assert iris.check_move(5.0) is True

    def test_check_move_at_min(self, iris):
        assert iris.check_move(1.0) is True

    def test_check_move_at_max(self, iris):
        assert iris.check_move(11.5) is True

    def test_check_move_below_min(self, iris):
        assert iris.check_move(0.5) is False

    def test_check_move_above_max(self, iris):
        assert iris.check_move(12.0) is False

    def test_pos_to_unit(self, iris):
        assert iris._pos_to_unit(0) == 0.0

    def test_unit_to_pos(self, iris):
        assert iris._unit_to_pos(0.0) == 0

    def test_get_aperture(self, iris):
        iris.controller.send_instruction.return_value = ("0", "PO", 0)
        assert iris.get_aperture() == 0.0

    def test_set_aperture_valid(self, iris):
        iris.controller.send_instruction.return_value = ("0", "PO", 0)
        # 5.0 is within [1.0, 11.5]
        result = iris.set_aperture(5.0)
        assert result is not None

    def test_set_aperture_out_of_range(self, iris):
        result = iris.set_aperture(0.5)
        assert result is None

    def test_shift_aperture_valid(self, iris):
        # get_aperture returns current position, then shift
        iris.controller.send_instruction.side_effect = [
            ("0", "PO", 98304),  # get_aperture → ~3.0
            ("0", "PO", 131072),  # shift result
        ]
        # current = 98304 / (32768*12) * 12 = 3.0, target = 3.0 + 1.0 = 4.0 (in range)
        result = iris.shift_aperture(1.0)
        assert result is not None

    def test_shift_aperture_out_of_range(self, iris):
        # current aperture is 11.0, shift +1.0 would be 12.0 (out of range)
        pulse_range = 32768 * 12
        pos_11 = int(11.0 / 12 * pulse_range)
        iris.controller.send_instruction.return_value = ("0", "PO", pos_11)
        result = iris.shift_aperture(1.0)
        assert result is None

    def test_backward_compat_aliases(self, iris):
        assert iris.pos_to_dist(0) == 0.0
        assert iris.dist_to_pos(0.0) == 0
        assert iris.extract_aperture_from_status(("0", "PO", 0)) == 0.0


# ===========================================================================
# Slider (ELL6 / ELL9)
# ===========================================================================

class TestSlider:
    @pytest.fixture
    def slider6(self):
        from elliptec.slider import Slider
        return _make_device(Slider, motor_type=6, pulse_per_rev=32768, range_=360)

    @pytest.fixture
    def slider9(self):
        from elliptec.slider import Slider
        return _make_device(Slider, motor_type=9, pulse_per_rev=32768, range_=360)

    # -- pos_to_slot / slot_to_pos --
    def test_pos_to_slot_exact(self, slider6):
        assert slider6.pos_to_slot(0) == 1
        assert slider6.pos_to_slot(31) == 2

    def test_pos_to_slot_close(self, slider6):
        # Within accuracy=5
        assert slider6.pos_to_slot(3) == 1

    def test_pos_to_slot_too_far(self, slider6):
        # 15 is too far from both 0 and 31
        assert slider6.pos_to_slot(15) is None

    def test_slot_to_pos(self, slider6):
        assert slider6.slot_to_pos(1) == 0
        assert slider6.slot_to_pos(2) == 31

    def test_slot_to_pos_out_of_range(self, slider6):
        assert slider6.slot_to_pos(5) is None

    def test_four_slot_positions(self, slider9):
        assert slider9.pos_to_slot(0) == 1
        assert slider9.pos_to_slot(32) == 2
        assert slider9.pos_to_slot(64) == 3
        assert slider9.pos_to_slot(96) == 4

    # -- get_slot / set_slot --
    def test_get_slot(self, slider6):
        slider6.controller.send_instruction.return_value = ("0", "PO", 0)
        assert slider6.get_slot() == 1

    def test_set_slot(self, slider6):
        slider6.controller.send_instruction.return_value = ("0", "PO", 31)
        assert slider6.set_slot(2) == 2

    def test_jog_forward(self, slider6):
        slider6.controller.send_instruction.return_value = ("0", "PO", 31)
        assert slider6.jog("forward") == 2

    def test_jog_invalid(self, slider6):
        assert slider6.jog("sideways") is None

    def test_extract_slot_none_status(self, slider6):
        assert slider6.extract_slot_from_status(None) is None

    def test_extract_slot_non_po(self, slider6):
        assert slider6.extract_slot_from_status(("0", "GS", "0")) is None


# ===========================================================================
# Shutter (2-position, based on ELL6)
# ===========================================================================

class TestShutter:
    @pytest.fixture
    def shutter(self):
        from elliptec.shutter import Shutter
        return _make_device(Shutter, motor_type=6, pulse_per_rev=32768, range_=31)

    @pytest.fixture
    def shutter_inv(self):
        from elliptec.shutter import Shutter
        return _make_device(Shutter, motor_type=6, pulse_per_rev=32768, range_=31, inverted=True)

    # -- pos_to_slot / slot_to_pos --
    def test_pos_to_slot(self, shutter):
        # range=31, slots=2, factor=31/1=31
        assert shutter.pos_to_slot(0) == 1
        assert shutter.pos_to_slot(31) == 2

    def test_slot_to_pos(self, shutter):
        assert shutter.slot_to_pos(1) == 0
        assert shutter.slot_to_pos(2) == 31

    # -- open / close --
    def test_open_normal(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 31)
        result = shutter.open()
        assert result == 2

    def test_close_normal(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 0)
        result = shutter.close()
        assert result == 1

    def test_open_inverted(self, shutter_inv):
        shutter_inv.controller.send_instruction.return_value = ("0", "PO", 0)
        result = shutter_inv.open()
        assert result == 1

    def test_close_inverted(self, shutter_inv):
        shutter_inv.controller.send_instruction.return_value = ("0", "PO", 31)
        result = shutter_inv.close()
        assert result == 2

    # -- is_open / is_closed --
    def test_is_open(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 31)
        assert shutter.is_open() is True

    def test_is_closed(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 0)
        assert shutter.is_closed() is True

    def test_is_open_inverted(self, shutter_inv):
        shutter_inv.controller.send_instruction.return_value = ("0", "PO", 0)
        assert shutter_inv.is_open() is True

    def test_is_closed_inverted(self, shutter_inv):
        shutter_inv.controller.send_instruction.return_value = ("0", "PO", 31)
        assert shutter_inv.is_closed() is True

    # -- set_slot edge cases --
    def test_set_slot_invalid(self, shutter):
        assert shutter.set_slot(3) is None

    def test_set_slot_1(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 0)
        assert shutter.set_slot(1) == 1

    def test_set_slot_2(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 31)
        assert shutter.set_slot(2) == 2

    # -- jog --
    def test_jog_forward(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 31)
        assert shutter.jog("forward") == 2

    def test_jog_backward(self, shutter):
        shutter.controller.send_instruction.return_value = ("0", "PO", 0)
        assert shutter.jog("backward") == 1

    def test_jog_invalid(self, shutter):
        assert shutter.jog("left") is None

    # -- extract_slot_from_status --
    def test_extract_slot_none(self, shutter):
        assert shutter.extract_slot_from_status(None) is None

    def test_extract_slot_non_po(self, shutter):
        assert shutter.extract_slot_from_status(("0", "GS", "0")) is None


# ===========================================================================
# Motor base class (tested via Rotator since Motor is abstract)
# ===========================================================================

class TestMotorBase:
    @pytest.fixture
    def motor(self):
        from elliptec.rotator import Rotator
        return _make_device(Rotator, motor_type=14, pulse_per_rev=32768, range_=360)

    def test_str(self, motor):
        s = str(motor)
        assert "Motor Type" in s
        assert "Serial No." in s

    def test_load_motor_info_none_raises(self):
        """If info comes back None, ExternalDeviceNotFound is raised."""
        from elliptec.rotator import Rotator
        from elliptec.errors import ExternalDeviceNotFound

        mock_ctrl = MagicMock()
        mock_ctrl.send_instruction.return_value = None

        with pytest.raises(ExternalDeviceNotFound):
            Rotator(controller=mock_ctrl, address="0", debug=True)

    def test_get_invalid_command(self, motor):
        result = motor.get("nonexistent_command")
        assert result is None

    def test_set_invalid_command(self, motor):
        result = motor.set("nonexistent_command")
        assert result is None

    def test_do_invalid_command(self, motor):
        result = motor.do("nonexistent_command")
        assert result is None

    def test_move_invalid_command(self, motor):
        result = motor.move("nonexistent_command")
        assert result is False

    def test_home_clockwise(self, motor):
        motor.controller.send_instruction.return_value = ("0", "PO", 0)
        motor.home(clockwise=True)
        # Verify ho0 was sent (home_clockwise -> b"ho0", then move adds "0" -> b"ho00")
        call_args = motor.controller.send_instruction.call_args
        assert b"ho0" in call_args[0][0] or call_args[0][0] == b"ho0"

    def test_home_anticlockwise(self, motor):
        motor.controller.send_instruction.return_value = ("0", "PO", 0)
        motor.home(clockwise=False)

    def test_save_user_data(self, motor):
        motor.controller.send_instruction.return_value = ("0", "GS", "0")
        motor.save_user_data()

    def test_change_address(self, motor):
        motor.controller.send_instruction.return_value = ("5", "GS", "0")
        motor.change_address("5")
        assert motor.address == "5"

    def test_close_connection(self, motor):
        motor.close_connection()
        motor.controller.close_connection.assert_called_once()


# ===========================================================================
# ContinuousMotor base (tested via Rotator)
# ===========================================================================

class TestContinuousMotorBase:
    @pytest.fixture
    def motor(self):
        from elliptec.rotator import Rotator
        return _make_device(Rotator, motor_type=14, pulse_per_rev=32768, range_=360)

    def test_jog_forward(self, motor):
        motor.controller.send_instruction.return_value = ("0", "PO", 16384)
        result = motor.jog("forward")
        assert result == 180.0

    def test_jog_backward(self, motor):
        motor.controller.send_instruction.return_value = ("0", "PO", 8192)
        result = motor.jog("backward")
        assert result == 90.0

    def test_jog_invalid(self, motor):
        assert motor.jog("sideways") is None

    def test_get_home_offset(self, motor):
        motor.controller.send_instruction.return_value = ("0", "HO", 0)
        assert motor.get_home_offset() == 0.0

    def test_set_home_offset(self, motor):
        motor.controller.send_instruction.return_value = ("0", "HO", 16384)
        motor.set_home_offset(180.0)

    def test_get_jog_step(self, motor):
        motor.controller.send_instruction.return_value = ("0", "GJ", 1000)
        result = motor.get_jog_step()
        assert result is not None

    def test_set_jog_step(self, motor):
        motor.controller.send_instruction.return_value = ("0", "GJ", 1000)
        motor.set_jog_step(10.0)

    def test_extract_unit_none(self, motor):
        assert motor._extract_unit_from_status(None) is None

    def test_extract_unit_wrong_code(self, motor):
        assert motor._extract_unit_from_status(("0", "GS", "0")) is None

    def test_extract_unit_po(self, motor):
        assert motor._extract_unit_from_status(("0", "PO", 32768)) == 360.0

    def test_extract_unit_ho(self, motor):
        assert motor._extract_unit_from_status(("0", "HO", 0)) == 0.0

    def test_extract_unit_gj(self, motor):
        assert motor._extract_unit_from_status(("0", "GJ", 1000)) is not None
