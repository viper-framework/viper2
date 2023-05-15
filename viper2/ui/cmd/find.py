import logging

from viper2.core.database import File
from viper2.core.sessions import sessions

from .command import Command, CommandRunError

log = logging.getLogger("viper")


class Find(Command):
    cmd = "find"
    description = "Find files stored in the database and local repository"

    def __init__(self) -> None:
        super().__init__()
        self.args_parser.add_argument(
            "key",
            nargs="?",
            choices=[
                "all",
                "name",
                "magic",
                "mime",
                "md5",
                "sha1",
                "sha256",
                "tag",
                "note",
                "ssdeep",
            ],
            help="search key",
        )
        self.args_parser.add_argument(
            "value", nargs="?", help="search value or pattern"
        )

    def run(self) -> None:
        try:
            super().run()
        except CommandRunError:
            return

        if self.args.key == "all":
            files = File.select().order_by(File.created_date)
        elif self.args.key == "name":
            files = File.select().where(File.name.contains(self.args.value))
        elif self.args.key == "magic":
            files = File.select().where(File.magic.contains(self.args.value))
        elif self.args.key == "mime":
            files = File.select().where(File.mime.contains(self.args.value))
        elif self.args.key == "md5":
            files = File.select().where(File.md5 == self.args.value)
        elif self.args.key == "sha1":
            files = File.select().where(File.sha1 == self.args.value)
        elif self.args.key == "sha256":
            files = File.select().where(File.sha256 == self.args.value)
        elif self.args.key == "sha512":
            files = File.select().where(File.sha512 == self.args.value)
        elif self.args.key == "tag":
            # TODO
            files = []
        elif self.args.key == "note":
            # TODO
            files = []
        elif self.args.key == "ssdeep":
            files = File.select().where(File.ssdeep.contains(self.args.value))

        if len(files) == 0:
            log.info("No matching results")
            return

        sessions.add_find(files)

        rows = []
        counter = 1
        for file in files:
            rows.append(
                [str(counter), str(file.created_date), file.name, file.sha1, file.magic]
            )
            counter += 1

        log.table(
            {"columns": ["#", "Date", "Name", "SHA1", "Magic", "Tags"], "rows": rows}
        )
