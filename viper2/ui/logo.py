# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from rich.console import Console

from ..common.version import VIPER_VERSION


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
