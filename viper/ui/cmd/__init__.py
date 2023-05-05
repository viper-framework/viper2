from .close import Close
from .info import Info
from .open import Open
from .sessions import Sessions


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
        Sessions.cmd: {
            "instance": Sessions(),
            "description": Sessions.description,
        },
    }
