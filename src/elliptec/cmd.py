""" This file contains a dictionary of commands that the devices can accept in
three different categories: get, set, move. For each command, it returns the
instruction code to send to the device. """
from __future__ import annotations

# TODO: Each type of device should get it's own list of supported commands.

get_: dict[str, bytes] = {
    "info": b"in",
    "status": b"gs",
    "position": b"gp",
    "stepsize": b"gj",
    "home_offset": b"go",
    "motor_1_info": b"i1",
    "motor_2_info": b"i2",
}

set_: dict[str, bytes] = {"stepsize": b"sj", "isolate": b"is", "address": b"ca", "home_offset": b"so"}

mov_: dict[str, bytes] = {
    "home_clockwise": b"ho0",
    "home_anticlockwise": b"ho1",
    "forward": b"fw",
    "backward": b"bw",
    "absolute": b"ma",
    "relative": b"mr",
}

do_: dict[str, bytes] = {
    "save_user_data": b"us",
    }


def commands() -> dict[str, dict[str, bytes]]:
    """Returns a dictionary of commands that the devices can accept."""
    return {"get": get_, "set": set_, "move": mov_, "do": do_}
