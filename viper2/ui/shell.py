# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import shlex
import subprocess
from typing import List, Tuple

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import clear as prompt_clear

from viper2 import printer

from ..core.database import File
from ..core.modules import load_modules, modules
from ..core.projects import projects
from ..core.sessions import sessions
from .cmd import load_commands
from .logo import logo


class Shell:
    def __init__(self, modules_path: str = "") -> None:
        self.__running: bool = True
        self.__commands: dict = {}
        self.__modules_path: str = modules_path
        self.__modules: dict = {}

    def __welcome(self) -> None:
        logo()

        printer.info(
            "[magenta]You have [bold]%d[/] file/s in your [bold]%s[/] project[/]",
            File.select().count(),
            projects.current.name,
        )

    def __prompt(self) -> List[Tuple[str, str]]:
        text = []
        if not projects.current.is_default():
            text.append(("bold ansicyan", f"{projects.current.name} "))

        text.append(("ansicyan", "viper "))

        if sessions.current:
            text.append(("ansigray", sessions.current.file.name))

            try:
                File.get(File.sha256 == sessions.current.file.sha256)
            except File.DoesNotExist:  # pylint: disable=no-member
                text.append(("ansimagenta", " [not stored]"))

        text.append(("ansicyan", "> "))
        return text

    def __expand_args(self, args: List[str]) -> List[str]:
        for index, arg in enumerate(args):
            if arg == "$file" and sessions.current:
                args[index] = sessions.current.file.path

        return args

    def exit(self) -> None:
        printer.info("Exiting...")
        self.__running = False

    def help(self) -> None:
        rows = [
            ["help", "Display this help message"],
            ["clear", "Clear the screen"],
            ["exit, quit", "Exit from the Viper shell"],
        ]
        for cmd_name, cmd_properties in self.__commands.items():
            rows.append([cmd_name, cmd_properties["description"]])

        printer.info("[bold]Commands:[/]")
        printer.table(columns=["Command", "Description"], rows=rows)

        print("")

        if len(self.__modules) == 0:
            printer.info("No modules available")
            return

        rows = []
        for module_name, module_properties in self.__modules.items():
            rows.append([module_name, module_properties["description"]])

        printer.info("[bold]Modules:[/]")
        printer.table(columns=["Module", "Description"], rows=rows)

    def clear(self) -> None:
        prompt_clear()

    def exec(self, cmd_name, cmd_args) -> None:
        with subprocess.Popen([cmd_name] + cmd_args, stdout=subprocess.PIPE) as proc:
            stdout, _ = proc.communicate()
            print(stdout.decode())

    def run(self) -> None:
        self.__welcome()

        self.__commands = load_commands()
        load_modules(self.__modules_path)
        self.__modules = modules

        session: PromptSession = PromptSession()

        while self.__running:
            try:
                self.__prompt()
                cmd_string = session.prompt(
                    self.__prompt(), auto_suggest=AutoSuggestFromHistory()
                )
            except KeyboardInterrupt:
                continue
            except EOFError:
                self.exit()
                continue

            if cmd_string.strip() == "":
                continue

            cmd_words = shlex.split(cmd_string)
            cmd_name = cmd_words[0].lower().strip()
            cmd_args = self.__expand_args(cmd_words[1:])

            if cmd_name.startswith("!"):
                self.exec(cmd_name[1:], cmd_args)
                continue

            if cmd_name in ("exit", "quit"):
                self.exit()
                continue

            if cmd_name == "help":
                self.help()
                continue

            if cmd_name == "clear":
                self.clear()
                continue

            if cmd_name in self.__commands:
                cmd = self.__commands[cmd_name]["class"]()
                cmd.add_args(*cmd_args)
                cmd.run()
                continue

            if cmd_name in self.__modules:
                mod = self.__modules[cmd_name]["class"]()
                mod.add_args(*cmd_args)
                mod.run()
                continue

            printer.error('No command or module found for "%s"', cmd_name)
