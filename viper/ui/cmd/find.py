import logging

from viper.core.database import Database

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
                "latest",
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

        db = Database()
        files = db.files.find(key=self.args.key, value=self.args.value)

        rows = []
        counter = 1
        for file in files:
            rows.append(
                [str(counter), str(file.created_at), file.name, file.sha1, file.magic]
            )
            counter += 1

        log.table({"columns": ["#", "Date", "Name", "SHA1", "Magic"], "rows": rows})
