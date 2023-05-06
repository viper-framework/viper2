import logging
import shlex

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console

from viper.core.projects import projects
from viper.core.sessions import sessions

from .cmd import commands
from .logger import init_logging
from .logo import logo

init_logging()

log = logging.getLogger("viper")


class Shell:
    def __init__(self) -> None:
        self.__running = True
        self.__commands = commands()

    def __prompt(self) -> None:
        project_name = ""
        if not projects.current.is_default():
            project_name = f"{projects.current.name} "

        file_name = ""
        if sessions.current:
            file_name = sessions.current.file.name

        console = Console()
        console.print(
            f"[bold cyan]{project_name}[/][cyan]viper[/] [white]{file_name}[/][cyan]>[/] ",
            end="",
        )

    def exit(self) -> None:
        log.info("Exiting...")
        self.__running = False

    def help(self) -> None:
        rows = [
            ["help", "Display this help message"],
            ["exit, quit", "Exit from the Viper shell"],
        ]
        for cmd_name, cmd_properties in self.__commands.items():
            rows.append([cmd_name, cmd_properties["description"]])

        log.info("[bold]Commands:[/]")
        log.table({"columns": ["Command", "Description"], "rows": rows})

    def run(self) -> None:
        logo()

        session = PromptSession()

        while self.__running:
            try:
                self.__prompt()
                cmd_string = session.prompt(auto_suggest=AutoSuggestFromHistory())
            except KeyboardInterrupt:
                continue
            except EOFError:
                self.exit()
                continue

            if cmd_string.strip() == "":
                continue

            cmd_words = shlex.split(cmd_string)
            cmd_name = cmd_words[0].lower().strip()
            cmd_args = cmd_words[1:]

            if cmd_name in ("exit", "quit"):
                self.exit()
                continue

            if cmd_name == "help":
                self.help()
                continue

            if cmd_name in self.__commands:
                cmd = self.__commands[cmd_name]["class"]()
                cmd.add_args(*cmd_args)
                cmd.run()
                continue

            log.error('No command or module found for "%s"', cmd_name)
