import argparse
from typing import Optional

from .exceptions import ArgumentError


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise ArgumentError()

    def exit(self, status: Optional[int] = 0, message: Optional[str] = None):
        raise ArgumentError()
