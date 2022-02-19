''' This devices serves as a database of supported devices and stores their
    properties, which are unavailable from the info of the device itself. '''

devices = {
    6: {
        'name': 'ELL6',
        'slots': 2,
        'positions': [0, 31],
        'commands': ['info', 'status', 'position', 'home', 'forward', 'backward'],
        'todo': ['open', 'close', 'disconnect', 'isolate', 'set_f_fwd', 'set_f_bck', 'fix_freqs', 'search_freqs'],
    },
    9: {
        'name': 'ELL9',
        'slots': 4,
        'positions': [0, 32, 64, 96],
        'commands': ['info', 'status', 'position', 'home', 'forward', 'backward'],
        'todo': ['open', 'close', 'disconnect', 'isolate', 'set_f_fwd', 'set_f_bck', 'fix_freqs', 'search_freqs'],
    },
    14: {
        'name': 'ELL14',
        'commands': ['info', 'status', 'position', 'home', 'forward', 'backward'],
        'todo': ['open', 'close', 'disconnect', 'isolate', 'set_f_fwd', 'set_f_bck', 'fix_freqs', 'search_freqs'],
    },
}