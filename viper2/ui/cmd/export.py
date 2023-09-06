import os
import shutil

from viper2 import printer
from viper2.common.errors import ERROR_NO_OPEN_FILE
from viper2.core.sessions import sessions

from .command import Command


class Export(Command):
    cmd = "export"
    description = "Export the currently open file to a destionation path"

    def __init__(self) -> None:
        super().__init__()
        self.args_parser.add_argument(
            "dst", help="Destination path to export the file to"
        )

    def run(self) -> None:
        super().run()

        if not sessions.current:
            printer.error(ERROR_NO_OPEN_FILE)
            return

        if not self.args.dst:
            printer.error("You need to specify a destionation path")
            return

        dst = self.args.dst

        # If the specified destination path exists and it is a folder, we use
        # the file name from the original file for the destination too.
        if os.path.isdir(self.args.dst):
            dst = os.path.join(self.args.dst, sessions.current.file.name)

        printer.info("Exporting file %s to %s", sessions.current.file.path, dst)
        shutil.copy2(sessions.current.file.path, dst)
