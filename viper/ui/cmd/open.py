import logging
import os
from typing import Any

from viper.common.exceptions import ArgumentErrorCallback
from viper.core.sessions import sessions

from .command import Command

log = logging.getLogger("viper")


class Open(Command):
    cmd = "open"
    description = "Open a session to a file"

    def __init__(self):
        super(Open, self).__init__()
        self.args.add_argument(
            "--file", "-f", action="store", help="Open the file specified at path"
        )

    def run(self, *args: Any):
        try:
            args = self.args.parse_args(args)
        except ArgumentErrorCallback:
            return

        if args.file:
            if not os.path.exists(args.file):
                log.error("The specified file at path %s does not exist", args.file)
                return

            sessions.new(args.file)
            return

        log.error("You need to specify how to open the file")

        try:
            self.args.print_usage()
        except ArgumentErrorCallback:
            pass
