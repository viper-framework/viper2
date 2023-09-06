from viper2 import printer
from viper2.core.database import File, Tag
from viper2.core.sessions import sessions

from .command import Command, CommandRunError


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

        match self.args.key:
            case "all":
                files = File.select().order_by(File.created_date)
            case "name":
                files = File.select().where(File.name.contains(self.args.value))
            case "magic":
                files = File.select().where(File.magic.contains(self.args.value))
            case "mime":
                files = File.select().where(File.mime.contains(self.args.value))
            case "md5":
                files = File.select().where(File.md5 == self.args.value)
            case "sha1":
                files = File.select().where(File.sha1 == self.args.value)
            case "sha256":
                files = File.select().where(File.sha256 == self.args.value)
            case "sha512":
                files = File.select().where(File.sha512 == self.args.value)
            case "tag":
                files = (
                    File.select()
                    .join(Tag, on=Tag.file == File.id)  # pylint: disable=no-member
                    .where(Tag.name.contains(self.args.value))
                )
            case "note":
                # TODO
                files = []
            case "ssdeep":
                files = File.select().where(File.ssdeep.contains(self.args.value))

        if len(files) == 0:
            printer.info("No matching results")
            return

        sessions.add_find(files)

        rows = []
        counter = 1
        for file in files:
            tags = ", ".join(tag.name for tag in file.tags)
            rows.append(
                [
                    str(counter),
                    str(file.created_date),
                    file.name,
                    file.sha1,
                    file.magic,
                    tags,
                ]
            )
            counter += 1

        printer.table(columns=["#", "Date", "Name", "SHA1", "Magic", "Tags"], rows=rows)
