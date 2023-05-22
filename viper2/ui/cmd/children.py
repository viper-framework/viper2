import logging

from viper2.core.database import File
from viper2.core.sessions import sessions

from .command import Command

log = logging.getLogger("viper")


class Children(Command):
    cmd = "children"
    description = "Get a list of the open file's children"

    def run(self) -> None:
        if not sessions.current:
            log.error("This command expects a session to a file to be open")
            return

        try:
            file = File.get(File.sha256 == sessions.current.file.sha256)
        except File.DoesNotExist:  # pylint: disable=no-member
            log.error("The currently open file is not stored")
            return

        rows = []
        for child in file.children:
            rows.append(
                [
                    str(child.created_date),
                    child.name,
                    child.sha1,
                    child.magic,
                    ", ".join(tag.name for tag in child.tags),
                ]
            )

        if len(rows) == 0:
            log.info("The currently open file does not have children")
            return

        log.table({"columns": ["Date", "Name", "SHA1", "Magic", "Tags"], "rows": rows})
