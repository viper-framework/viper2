# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from viper2 import printer
from viper2.common.errors import ERROR_NO_OPEN_FILE
from viper2.core.database import File
from viper2.core.sessions import sessions

from .command import Command


class Parent(Command):
    cmd = "parent"
    description = "Specify a parent to the currently open file"

    def __init__(self) -> None:
        super().__init__()
        subparsers = self.args_parser.add_subparsers(dest="subname")
        subparsers.add_parser("delete", help="Delete the existing parent")
        add = subparsers.add_parser(
            "add", help="Add a parent ot the currently open file"
        )
        add.add_argument("parent", help="SHA256 hash of the parent")

    def run(self) -> None:
        super().run()

        if not sessions.current:
            printer.error(ERROR_NO_OPEN_FILE)
            return

        try:
            file = File.get(File.sha256 == sessions.current.file.sha256)
        except File.DoesNotExist:  # pylint: disable=no-member
            printer.error(
                'The currently open file is not stored, use "store" command first'
            )
            return

        if self.args.subname == "delete":
            file.parent = None
            file.save()
            printer.success("Parent successfully deleted")
        elif self.args.subname == "add":
            if file.parent:
                printer.error("The currently open file already has a parent!")
                return

            if self.args.parent == sessions.current.file.sha256:
                printer.error(
                    "The specified parent is the same as the currently open file"
                )
                return

            try:
                parent = File.get(File.sha256 == self.args.parent)
            except File.DoesNotExist:  # pylint: disable=no-member
                printer.error(
                    "The specified parent with hash %s does not exist", self.args.parent
                )
                return

            file.parent = parent
            file.save()

            printer.success("Successfully added parent")
        else:
            if not file.parent:
                printer.info("The currently open file does not have a parent")
            else:
                printer.table(
                    columns=["Date", "Name", "SHA1", "Magic", "Tags"],
                    rows=[
                        [
                            str(file.parent.created_date),
                            file.parent.name,
                            file.parent.sha1,
                            file.parent.magic,
                            ", ".join(tag.name for tag in file.parent.tags),
                        ]
                    ],
                )
