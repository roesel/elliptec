"""Unit tests for elliptec that can run without hardware (CI-safe)."""
import pytest

from elliptec.tools import parse, s32, is_metric, is_null_or_empty, error_check, move_check
from elliptec.cmd import commands, get_, set_, mov_, do_
from elliptec.devices import devices
from elliptec.errcodes import error_codes
from elliptec.errors import ExternalDeviceNotFound


# ── tools.s32 ──────────────────────────────────────────────────────────────

class TestS32:
    def test_zero(self):
        assert s32(0) == 0

    def test_positive(self):
        assert s32(0x00000064) == 100

    def test_negative(self):
        assert s32(0xFFFFFF9C) == -100

    def test_max_positive(self):
        assert s32(0x7FFFFFFF) == 2147483647

    def test_min_negative(self):
        assert s32(0x80000000) == -2147483648


# ── tools.is_metric ────────────────────────────────────────────────────────

class TestIsMetric:
    def test_metric(self):
        assert is_metric("0") == "Metric"

    def test_imperial(self):
        assert is_metric("1") == "Imperial"

    def test_unknown(self):
        assert is_metric("2") is None


# ── tools.is_null_or_empty ─────────────────────────────────────────────────

class TestIsNullOrEmpty:
    def test_empty(self):
        assert is_null_or_empty(b"") is True

    def test_no_terminator(self):
        assert is_null_or_empty(b"0PO00000000") is True

    def test_valid(self):
        assert is_null_or_empty(b"0PO00000000\r\n") is False


# ── tools.parse ────────────────────────────────────────────────────────────

class TestParse:
    def test_returns_none_for_incomplete(self):
        assert parse(b"", debug=False) is None
        assert parse(b"no terminator", debug=False) is None

    def test_parse_position(self):
        # Address 0, code PO, position 0x00000064 = 100
        result = parse(b"0PO00000064\r\n", debug=False)
        assert result == ("0", "PO", 100)

    def test_parse_position_negative(self):
        # 0xFFFFFF9C = -100 in signed 32-bit
        result = parse(b"0POFFFFFF9C\r\n", debug=False)
        assert result == ("0", "PO", -100)

    def test_parse_home_offset(self):
        result = parse(b"0HO00000000\r\n", debug=False)
        assert result == ("0", "HO", 0)

    def test_parse_backward_position(self):
        result = parse(b"0BO000000C8\r\n", debug=False)
        assert result == ("0", "BO", 200)

    def test_parse_general_status_ok(self):
        result = parse(b"0GS00\r\n", debug=False)
        assert result == ("0", "GS", "0")

    def test_parse_general_status_error(self):
        # Error code 0x09 = 9 (Busy)
        result = parse(b"0GS09\r\n", debug=False)
        assert result == ("0", "GS", "9")

    def test_parse_info(self):
        # Construct a valid IN response
        # Address=0, Code=IN, MotorType=0E (14), Serial=12345678
        # Year=2023, Firmware=01, Thread=0 (Metric), Hardware=1
        # Range=0168 (360), PulsePerRev=00008000 (32768)
        msg = b"0IN0E1234567820230101016800008000\r\n"
        result = parse(msg, debug=False)
        assert isinstance(result, dict)
        assert result["Address"] == "0"
        assert result["Motor Type"] == 14
        assert result["Serial No."] == "12345678"
        assert result["Range"] == 360
        assert result["Pulse/Rev"] == 32768
        assert result["Thread"] == "Metric"

    def test_parse_invalid_address(self):
        with pytest.raises(ValueError, match="Invalid Address"):
            parse(b"XPO00000000\r\n", debug=False)

    def test_parse_hex_address(self):
        result = parse(b"APO00000064\r\n", debug=False)
        assert result == ("A", "PO", 100)

    def test_parse_unknown_code(self):
        result = parse(b"0ZZ12345\r\n", debug=False)
        assert result == ("0", "ZZ", "12345")


# ── tools.error_check / move_check ─────────────────────────────────────────

class TestErrorCheck:
    def test_status_ok(self, caplog):
        error_check(("0", "GS", "0"))
        # Should not log error
        assert "ERROR" not in caplog.text

    def test_status_error(self, caplog):
        import logging
        with caplog.at_level(logging.ERROR):
            error_check(("0", "GS", "9"))
        assert "Busy" in caplog.text

    def test_none_status(self, caplog):
        import logging
        with caplog.at_level(logging.WARNING):
            error_check(None)
        assert "None" in caplog.text

    def test_position_status(self, caplog):
        import logging
        with caplog.at_level(logging.DEBUG):
            error_check(("0", "PO", 100))


class TestMoveCheck:
    def test_move_successful_po(self, caplog):
        import logging
        with caplog.at_level(logging.DEBUG):
            move_check(("0", "PO", 100))
        assert "Successful" in caplog.text

    def test_move_successful_bo(self, caplog):
        import logging
        with caplog.at_level(logging.DEBUG):
            move_check(("0", "BO", 200))
        assert "Successful" in caplog.text

    def test_move_none(self, caplog):
        import logging
        with caplog.at_level(logging.WARNING):
            move_check(None)
        assert "None" in caplog.text


# ── cmd ────────────────────────────────────────────────────────────────────

class TestCommands:
    def test_commands_returns_all_categories(self):
        cmds = commands()
        assert set(cmds.keys()) == {"get", "set", "move", "do"}

    def test_get_commands(self):
        assert get_["info"] == b"in"
        assert get_["status"] == b"gs"
        assert get_["position"] == b"gp"

    def test_set_commands(self):
        assert set_["stepsize"] == b"sj"
        assert set_["address"] == b"ca"

    def test_move_commands(self):
        assert mov_["home_clockwise"] == b"ho0"
        assert mov_["absolute"] == b"ma"
        assert mov_["forward"] == b"fw"

    def test_do_commands(self):
        assert do_["save_user_data"] == b"us"


# ── devices ────────────────────────────────────────────────────────────────

class TestDevices:
    def test_known_devices_exist(self):
        assert 6 in devices   # ELL6
        assert 9 in devices   # ELL9
        assert 14 in devices  # ELL14
        assert 18 in devices  # ELL18
        assert 20 in devices  # ELL20

    def test_device_has_required_fields(self):
        for dev_id, dev in devices.items():
            assert "name" in dev, f"Device {dev_id} missing name"
            assert "description" in dev, f"Device {dev_id} missing description"
            assert "commands" in dev, f"Device {dev_id} missing commands"

    def test_slider_has_positions(self):
        assert devices[6]["slots"] == 2
        assert devices[6]["positions"] == [0, 31]
        assert devices[9]["slots"] == 4
        assert len(devices[9]["positions"]) == 4


# ── errcodes ───────────────────────────────────────────────────────────────

class TestErrorCodes:
    def test_status_ok(self):
        assert error_codes["0"] == "Status OK"

    def test_known_codes(self):
        assert "Timeout" in error_codes["1"]
        assert "Busy" in error_codes["9"]
        assert len(error_codes) == 14


# ── errors ─────────────────────────────────────────────────────────────────

class TestErrors:
    def test_external_device_not_found_is_ioerror(self):
        assert issubclass(ExternalDeviceNotFound, IOError)

    def test_can_raise(self):
        with pytest.raises(ExternalDeviceNotFound):
            raise ExternalDeviceNotFound("test")
