from typing import Any

from viper.common.arguments import ArgumentError, ArgumentParser
from viper.common.file import FileObject


class ModuleRunError(Exception):
    pass


class Module:
    cmd = ""
    description = ""

    def __init__(self) -> None:
        self.args = None
        self.__args_input = None
        self.args_parser = ArgumentParser(prog=self.cmd, description=self.description)

    def add_args(self, *args: Any) -> None:
        self.__args_input = args

    @staticmethod
    def supports_file(file_object: FileObject) -> bool:
        raise NotImplementedError

    def run(self) -> None:
        try:
            self.args = self.args_parser.parse_args(self.__args_input)
        except ArgumentError as exc:
            raise ModuleRunError() from exc
