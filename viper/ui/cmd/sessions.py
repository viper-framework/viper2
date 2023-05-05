import logging

from viper.core.sessions import sessions

from .command import Command, CommandRunError

log = logging.getLogger("viper")


class Sessions(Command):
    cmd = "sessions"
    description = "List or switch sessions"

    def __init__(self):
        super(Sessions, self).__init__()
        group = self.args_parser.add_mutually_exclusive_group()
        group.add_argument(
            "-l", "--list", action="store_true", help="List all existing sessions"
        )
        group.add_argument(
            "-s", "--switch", type=int, help="Switch to the specified session"
        )

    def run(self):
        try:
            super(Sessions, self).run()
        except CommandRunError:
            return

        if self.args.list:
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
                        str(session.id),
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
            return

        if self.args.switch:
            for session in sessions.list():
                if self.args.switch == session.id:
                    sessions.switch(session)
                    return

            log.error("The specified session ID doesn't seem to exist")
            return

        self.args_parser.print_usage()
