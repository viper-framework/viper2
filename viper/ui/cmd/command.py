from typing import Any

from viper.common.arguments import ArgumentParser


class Command:
    cmd = ""
    description = ""

    def __init__(self):
        self.argparser = ArgumentParser(prog=self.cmd, description=self.description)

    def run(self, *args: Any):
        raise NotImplementedError
