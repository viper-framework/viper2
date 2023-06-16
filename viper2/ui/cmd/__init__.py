from .about import About
from .children import Children
from .close import Close
from .export import Export
from .find import Find
from .info import Info
from .open import Open
from .parent import Parent
from .projects import Projects
from .sessions import Sessions
from .store import Store
from .tags import Tags


def load_commands() -> dict:
    return {
        About.cmd: {"class": About, "description": About.description},
        Children.cmd: {"class": Children, "description": Children.description},
        Close.cmd: {"class": Close, "description": Close.description},
        Export.cmd: {"class": Export, "description": Export.description},
        Info.cmd: {"class": Info, "description": Info.description},
        Find.cmd: {"class": Find, "description": Find.description},
        Open.cmd: {"class": Open, "description": Open.description},
        Parent.cmd: {"class": Parent, "description": Parent.description},
        Projects.cmd: {"class": Projects, "description": Projects.description},
        Sessions.cmd: {"class": Sessions, "description": Sessions.description},
        Store.cmd: {"class": Store, "description": Store.description},
        Tags.cmd: {"class": Tags, "description": Tags.description},
    }
