from typing import Any

from viper.common.arguments import ArgumentError, ArgumentParser


class CommandRunError(Exception):
    pass


class Command:
    cmd = ""
    description = ""

    def __init__(self):
        self.args = None
        self.__args_input = None
        self.args_parser = ArgumentParser(prog=self.cmd, description=self.description)

    def add_args(self, *args: Any):
        self.__args_input = args

    def run(self):
        try:
            self.args = self.args_parser.parse_args(self.__args_input)
        except ArgumentError:
            raise CommandRunError()
