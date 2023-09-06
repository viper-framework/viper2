# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import platform
import sys

from viper2 import printer
from viper2.common.version import VIPER_VERSION

from .command import Command


class About(Command):
    cmd = "about"
    description = "Show information about Viper 2"

    def run(self) -> None:
        rows = []
        rows.append(["Viper Version", VIPER_VERSION])
        rows.append(["Python executable", sys.executable])
        rows.append(["Python Version", platform.python_version()])

        printer.table(columns=["Key", "Value"], rows=rows)
