# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import cast

from viper2 import printer
from viper2.common.errors import ERROR_NO_OPEN_FILE
from viper2.common.module import Module
from viper2.core.database import File, Tag
from viper2.core.modules import modules
from viper2.core.sessions import sessions

from .command import Command


class Info(Command):
    cmd = "info"
    description = "Show information on the open file"

    def run(self) -> None:
        if not sessions.current:
            printer.error(ERROR_NO_OPEN_FILE)
            return

        try:
            file = File.get(File.sha256 == sessions.current.file.sha256)
            tags = Tag.select().where(Tag.file == file)
        except File.DoesNotExist:  # pylint: disable=no-member
            tags_string = ""
        else:
            tags_string = ", ".join(tag.name for tag in list(tags))

        printer.table(
            columns=["Key", "Value"],
            rows=[
                ["Name", sessions.current.file.name],
                ["Tags", tags_string],
                ["Path", sessions.current.file.path],
                ["Size", str(sessions.current.file.size)],
                ["Magic", sessions.current.file.magic],
                ["Mime", sessions.current.file.mime],
                ["MD5", sessions.current.file.md5],
                ["SHA1", sessions.current.file.sha1],
                ["SHA256", sessions.current.file.sha256],
                ["SHA512", sessions.current.file.sha512],
                ["SSdeep", sessions.current.file.ssdeep],
                ["CRC32", sessions.current.file.crc32],
            ],
        )

        supported_modules = []
        for module_name, module_properties in modules.items():
            mod = cast(Module, module_properties["class"])
            try:
                if mod.supports_file(sessions.current.file):
                    supported_modules.append(
                        [module_name, module_properties["description"]]
                    )
            except NotImplementedError:
                pass

        if len(supported_modules) > 0:
            print("")

            printer.info("The following modules support the analysis of this file:")
            printer.table(columns=["Module", "Description"], rows=supported_modules)
