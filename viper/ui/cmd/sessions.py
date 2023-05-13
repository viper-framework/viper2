import logging

from viper.core.sessions import sessions

from .command import Command, CommandRunError

log = logging.getLogger("viper")


class Sessions(Command):
    cmd = "sessions"
    description = "List or switch sessions"

    def __init__(self) -> None:
        super().__init__()
        group = self.args_parser.add_mutually_exclusive_group()
        group.add_argument(
            "-l", "--list", action="store_true", help="list all existing sessions"
        )
        group.add_argument(
            "-s", "--switch", type=int, help="switch to the specified session"
        )

    def __list(self) -> None:
        if not sessions.list():
            log.info("There are no open sessions")
            return

        rows = []
        for session in sessions.list():
            current = ""
            if session == sessions.current:
                current = "Yes"

            rows.append(
                [
                    str(session.identifier),
                    session.file.name,
                    session.file.sha1,
                    session.created_at,
                    current,
                ]
            )

        log.info("[bold]Open sessions:[/]")
        log.table(
            {
                "columns": ["#", "Name", "SHA1", "Created At", "Current"],
                "rows": rows,
            },
        )

    def __switch(self, identifier: int) -> None:
        for session in sessions.list():
            if identifier == session.identifier:
                sessions.switch(session)
                return

        log.error("The specified session ID doesn't seem to exist")

    def run(self) -> None:
        try:
            super().run()
        except CommandRunError:
            return

        if self.args.list:
            self.__list()
        elif self.args.switch:
            self.__switch(self.args.switch)
        else:
            self.args_parser.print_usage()
