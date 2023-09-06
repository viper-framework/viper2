import logging
from typing import cast

from viper2.common.errors import ERROR_NO_OPEN_FILE
from viper2.common.module import Module
from viper2.core.database import File, Tag
from viper2.core.modules import modules
from viper2.core.sessions import sessions

from .command import Command

log = logging.getLogger("viper")


class Info(Command):
    cmd = "info"
    description = "Show information on the open file"

    def run(self) -> None:
        if not sessions.current:
            log.error(ERROR_NO_OPEN_FILE)
            return

        try:
            file = File.get(File.sha256 == sessions.current.file.sha256)
            tags = Tag.select().where(Tag.file == file)
        except File.DoesNotExist:  # pylint: disable=no-member
            tags_string = ""
        else:
            tags_string = ", ".join(tag.name for tag in list(tags))

        log.table(
            {
                "columns": ["Key", "Value"],
                "rows": [
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
            },
        )

        supported_modules = []
        for module_name, module_properties in modules.items():
            mod = cast(Module, module_properties["class"])
            if mod.supports_file(sessions.current.file):
                supported_modules.append(
                    [module_name, module_properties["description"]]
                )

        if len(supported_modules) > 0:
            print("")

            log.info("The following modules support the analysis of this file:")
            log.table({"columns": ["Module", "Description"], "rows": supported_modules})
