import logging
import platform
import sys

from viper2.common.version import VIPER_VERSION

from .command import Command

log = logging.getLogger("viper")


class About(Command):
    cmd = "about"
    description = "Show information about Viper 2"

    def run(self) -> None:
        rows = []
        rows.append(["Viper Version", VIPER_VERSION])
        rows.append(["Python executable", sys.executable])
        rows.append(["Python Version", platform.python_version()])

        log.table({"columns": ["Key", "Value"], "rows": rows})
