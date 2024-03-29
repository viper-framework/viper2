# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import peewee

from viper2 import printer
from viper2.common.errors import ERROR_NO_OPEN_FILE
from viper2.core.database import File, Tag
from viper2.core.sessions import sessions

from .command import Command, CommandRunError


class Tags(Command):
    cmd = "tags"
    description = "Tag files in the database"

    def __init__(self) -> None:
        super().__init__()
        subparsers = self.args_parser.add_subparsers(dest="subname")
        subparsers.add_parser("list", help="List all existing tags")
        add = subparsers.add_parser("add", help="Add one or more tags to open file")
        add.add_argument(
            "-t", "--tag", action="append", help="Specify a tag", required=True
        )

    def list(self) -> None:
        tags = Tag.select(Tag.name).distinct(True)
        for tag in list(tags):
            print(tag.name)

    def add(self, tags) -> None:
        if not sessions.current:
            printer.error(ERROR_NO_OPEN_FILE)
            return

        try:
            file = File.get(File.sha256 == sessions.current.file.sha256)
        except File.DoesNotExist:  # pylint: disable=no-member
            printer.error(
                "The currently open file is not stored in the database, "
                'use "store" command first'
            )
            return

        for tag in tags:
            try:
                new_tag = Tag(name=tag, file=file)
                new_tag.save()
            except peewee.IntegrityError:
                printer.error('The tag "%s" already exists', tag)

    def run(self) -> None:
        try:
            super().run()
        except CommandRunError:
            return

        if self.args.subname == "list":
            self.list()
        elif self.args.subname == "add":
            self.add(self.args.tag)
