import os

from viper2 import printer
from viper2.core.projects import projects
from viper2.core.sessions import sessions
from viper2.core.storage import Storage

from .command import Command, CommandRunError


class Open(Command):
    cmd = "open"
    description = "Open a session to a file"

    def __init__(self) -> None:
        super().__init__()
        self.args_parser.add_argument(
            "-f", "--file", action="store", help="open the file specified at path"
        )
        self.args_parser.add_argument(
            "-l",
            "--last",
            action="store",
            help="# of a result from the last `find` command",
        )

    def run(self) -> None:
        try:
            super().run()
        except CommandRunError:
            return

        if self.args.file:
            if not os.path.exists(self.args.file):
                printer.error(
                    "The specified file at path %s does not exist", self.args.file
                )
                return

            sessions.new(self.args.file)
        elif self.args.last:
            for idx, entry in enumerate(sessions.get_find(), start=1):
                if idx == int(self.args.last):
                    sessions.new(
                        Storage().get_file_path(
                            projects.current.path, str(entry.sha256)
                        )
                    )
                    return

            printer.error("Did not find a last find entry with the provided #")
        else:
            self.args_parser.print_usage()
