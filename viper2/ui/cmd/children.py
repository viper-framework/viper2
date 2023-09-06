# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from viper2 import printer
from viper2.common.errors import ERROR_NO_OPEN_FILE
from viper2.core.database import File
from viper2.core.sessions import sessions

from .command import Command


class Children(Command):
    cmd = "children"
    description = "Get a list of the open file's children"

    def run(self) -> None:
        if not sessions.current:
            printer.error(ERROR_NO_OPEN_FILE)
            return

        try:
            file = File.get(File.sha256 == sessions.current.file.sha256)
        except File.DoesNotExist:  # pylint: disable=no-member
            printer.error("The currently open file is not stored")
            return

        rows = []
        for child in file.children:
            rows.append(
                [
                    str(child.created_date),
                    child.name,
                    child.sha1,
                    child.magic,
                    ", ".join(tag.name for tag in child.tags),
                ]
            )

        if len(rows) == 0:
            printer.info("The currently open file does not have children")
            return

        printer.table(columns=["Date", "Name", "SHA1", "Magic", "Tags"], rows=rows)
