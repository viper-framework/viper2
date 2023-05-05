import argparse
import logging
from typing import Optional

from .exceptions import ArgumentErrorCallback

log = logging.getLogger("viper")


class ArgumentParser(argparse.ArgumentParser):
    def print_usage(self, file: Optional[str] = None):
        log.info(self.format_usage())
        raise ArgumentErrorCallback("")

    def print_help(self, file: Optional[str] = None):
        log.info(self.format_help())
        raise ArgumentErrorCallback("")

    def error(self, message: str):
        raise ArgumentErrorCallback(message, "error")

    def exit(self, status: Optional[int] = 0, message: Optional[str] = None):
        if message:
            raise ArgumentErrorCallback(message)
