from .close import Close
from .info import Info
from .open import Open


def commands():
    return {
        Open.cmd: {
            "instance": Open(),
            "description": Open.description,
        },
        Info.cmd: {
            "instance": Info(),
            "description": Info.description,
        },
        Close.cmd: {
            "instance": Close(),
            "description": Close.description,
        },
    }
