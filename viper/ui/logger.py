import logging
from functools import partial, partialmethod
from logging import StreamHandler

from rich.console import Console
from rich.table import Table


class ShellHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)

    def emit(self, record):
        console = Console()

        if record.levelno == logging.DEBUG:
            console.print(record.msg)
        elif record.levelno == logging.INFO:
            console.print(record.msg)
        elif record.levelno == logging.TABLE:
            table = Table(show_header=True, header_style="bold")

            for column in record.msg.get("columns"):
                table.add_column(column)

            for row in record.msg.get("rows"):
                table.add_row(*row)

            console.print(table)
        elif record.levelno == logging.SUCCESS:
            console.print(f"[green]{record.msg}[/]")
        elif record.levelno == logging.WARNING:
            console.print(f"[yellow]WARNING: {record.msg}[/]")
        elif record.levelno == logging.ERROR:
            console.print(f"[red]ERROR: {record.msg}[/]")
        elif record.levelno == logging.CRITICAL:
            console.print(f"[red]CRITICAL: {record.msg}[/]")
        elif record.levelno == logging.FATAL:
            console.print(f"[red]FATAL: {record.msg}[/]")


def init_logging():
    logging.basicConfig(level=logging.INFO)

    logging.TABLE = 21
    logging.addLevelName(logging.TABLE, "TABLE")
    logging.Logger.table = partialmethod(logging.Logger.log, logging.TABLE)
    logging.table = partial(logging.log, logging.TABLE)

    logging.SUCCESS = 22
    logging.addLevelName(logging.SUCCESS, "SUCCESS")
    logging.Logger.success = partialmethod(logging.Logger.log, logging.SUCCESS)
    logging.success = partial(logging.log, logging.SUCCESS)

    log = logging.getLogger("viper")
    log.propagate = False
    log.addHandler(ShellHandler())
