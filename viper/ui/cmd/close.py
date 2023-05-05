from typing import Any

from viper.core.sessions import sessions

from .command import Command


class Close(Command):
    cmd = "close"
    description = "Close the current session"

    def run(self, *args: Any):
        sessions.close()
