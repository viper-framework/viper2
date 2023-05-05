import logging
import shlex

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console

from viper.core.sessions import sessions

from .cmd import commands
from .logger import init_logging
from .logo import logo

init_logging()

log = logging.getLogger("viper")


class Shell:
    def __init__(self):
        self.__running = True
        self.__commands = commands()

    def __prompt(self):
        file_name = ""
        if sessions.current:
            file_name = sessions.current.file.name

        console = Console()
        console.print(f"[cyan]viper[/] [white]{file_name}[/][cyan]>[/] ", end="")

    def exit(self):
        log.info("Exiting...")
        self.__running = False

    def help(self):
        rows = [
            ["help", "Display this help message"],
            ["exit, quit", "Exit from the Viper shell"],
        ]
        for cmd in self.__commands:
            rows.append([cmd, self.__commands[cmd]["description"]])

        log.info("[bold]Commands:[/]")
        log.table({"columns": ["Command", "Description"], "rows": rows})

    def run(self):
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

            if cmd_name == "exit" or cmd_name == "quit":
                self.exit()
                continue

            if cmd_name == "help":
                self.help()
                continue

            if cmd_name in self.__commands.keys():
                cmd = self.__commands[cmd_name]["class"]()
                cmd.run(*cmd_args)
                continue

            log.error(f'No command or module found for "{cmd_name}"')
