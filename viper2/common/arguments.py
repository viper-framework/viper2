import argparse
from typing import Optional


class ArgumentError(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise ArgumentError()

    def exit(self, status: Optional[int] = 0, message: Optional[str] = None):
        raise ArgumentError()
