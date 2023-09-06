# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from viper2.core.sessions import sessions

from .command import Command


class Close(Command):
    cmd = "close"
    description = "Close the current session"

    def run(self) -> None:
        sessions.close()
