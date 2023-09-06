# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import argparse
from typing import Optional


class ArgumentError(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise ArgumentError()

    def exit(self, status: Optional[int] = 0, message: Optional[str] = None):
        raise ArgumentError()
