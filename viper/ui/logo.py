from rich.console import Console

from viper.common.version import VIPER_VERSION


def logo():
    console = Console()
    console.print(
        f"""
[red]  ██    ██ ██ ██████  ███████ ██████ [/]
[yellow]  ██    ██ ██ ██   ██ ██      ██   ██[/]
[green]  ██    ██ ██ ██████  █████   ██████ [/]
[blue]   ██  ██  ██ ██      ██      ██   ██[/]
[magenta]    ████   ██ ██      ███████ ██   ██[/]  [white]v{VIPER_VERSION}[/]
"""
    )
