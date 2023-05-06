import logging

from viper.core.modules import modules
from viper.core.sessions import sessions

from .command import Command

log = logging.getLogger("viper")


class Info(Command):
    cmd = "info"
    description = "Show information on the open file"

    def run(self) -> None:
        if not sessions.current:
            log.error("No open session! This command expects a file to be open")
            return

        log.table(
            {
                "columns": ["Key", "Value"],
                "rows": [
                    ["Name", sessions.current.file.name],
                    ["Tags", sessions.current.file.tags],
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
                    ["Parent", sessions.current.file.parent],
                    ["Children", sessions.current.file.children],
                ],
            },
        )

        supported_modules = []
        for module_name, module_properties in modules.items():
            if module_properties["class"].supports_file(sessions.current.file):
                supported_modules.append(
                    [module_name, module_properties["description"]]
                )

        if len(supported_modules) > 0:
            print("")

            log.info(
                "The following modules indicated they support analyzing this file:"
            )
            log.table({"columns": ["Module", "Description"], "rows": supported_modules})
