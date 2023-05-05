import logging
from typing import Any

from viper.core.sessions import sessions
from viper.common.exceptions import ArgumentError

from .command import Command

log = logging.getLogger("viper")

class Sessions(Command):
    cmd = "sessions"
    description = "List or switch sessions"

    def __init__(self):
        super(Sessions, self).__init__()
        group = self.argparser.add_mutually_exclusive_group()
        group.add_argument(
            "-l", "--list", action="store_true", help="List all existing sessions"
        )
        group.add_argument(
            "-s", "--switch", type=int, help="Switch to the specified session"
        )

    def run(self, *args: Any):
        try:
            args = self.argparser.parse_args(args)
        except ArgumentError:
            return

        if args.list:
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
        elif args.switch:
            for session in sessions.list():
                if args.switch == session.id:
                    sessions.switch(session)
                    return

            log.error("The specified session ID doesn't seem to exist")
        else:
            self.argparser.print_usage()
