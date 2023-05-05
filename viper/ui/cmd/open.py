import logging
import os

from viper.core.sessions import sessions

from .command import Command, CommandRunError

log = logging.getLogger("viper")


class Open(Command):
    cmd = "open"
    description = "Open a session to a file"

    def __init__(self):
        super(Open, self).__init__()
        self.args_parser.add_argument(
            "--file", "-f", action="store", help="Open the file specified at path"
        )

    def run(self):
        try:
            super(Open, self).run()
        except CommandRunError:
            return

        if self.args.file:
            if not os.path.exists(self.args.file):
                log.error(
                    "The specified file at path %s does not exist", self.args.file
                )
                return

            sessions.new(self.args.file)
            return

        self.args_parser.print_usage()
