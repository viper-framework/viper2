from .close import Close
from .info import Info
from .open import Open
from .projects import Projects
from .sessions import Sessions


def commands():
    return {
        Open.cmd: {"class": Open, "description": Open.description},
        Info.cmd: {"class": Info, "description": Info.description},
        Close.cmd: {"class": Close, "description": Close.description},
        Sessions.cmd: {"class": Sessions, "description": Sessions.description},
        Projects.cmd: {"class": Projects, "description": Projects.description},
    }
