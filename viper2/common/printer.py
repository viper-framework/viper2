from typing import Any

from rich.console import Console
from rich.table import Table


class Printer:
    def __init__(self):
        self.__console = Console()

    def info(self, msg: str, *args: Any) -> None:
        self.__console.print(msg % args)

    def warning(self, msg: str, *args: Any) -> None:
        self.__console.print(f"[yellow]WARNING: {msg % args}[/]")

    def error(self, msg: str, *args: Any) -> None:
        self.__console.print(f"[red]ERROR: {msg % args}[/]")

    def success(self, msg: str, *args: Any) -> None:
        self.__console.print(f"[green]{msg % args}[/]")

    def table(self, columns, rows) -> None:
        table = Table(show_header=True, header_style="bold")

        for column in columns:
            table.add_column(column)

        for row in rows:
            table.add_row(*row)

        self.__console.print(table)
