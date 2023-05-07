from .close import Close
from .find import Find
from .info import Info
from .open import Open
from .projects import Projects
from .sessions import Sessions
from .store import Store


def load_commands():
    return {
        Close.cmd: {"class": Close, "description": Close.description},
        Info.cmd: {"class": Info, "description": Info.description},
        Find.cmd: {"class": Find, "description": Find.description},
        Open.cmd: {"class": Open, "description": Open.description},
        Projects.cmd: {"class": Projects, "description": Projects.description},
        Sessions.cmd: {"class": Sessions, "description": Sessions.description},
        Store.cmd: {"class": Store, "description": Store.description},
    }
