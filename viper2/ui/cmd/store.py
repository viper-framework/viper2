import logging

from viper2.common.file import FileObject
from viper2.core.database import File
from viper2.core.projects import projects
from viper2.core.sessions import sessions
from viper2.core.storage import Storage

from .command import Command, CommandRunError

log = logging.getLogger("viper")


class Store(Command):
    cmd = "store"
    description = "Store one or multiple files in the database and the local repository"

    def add_file(self, file_object: FileObject) -> None:
        try:
            File.get(File.sha256 == file_object.sha256)
        except File.DoesNotExist:  # pylint: disable=no-member
            file = File(
                name=file_object.name,
                size=file_object.size,
                magic=file_object.magic,
                mime=file_object.mime,
                md5=file_object.md5,
                crc32=file_object.crc32,
                sha1=file_object.sha1,
                sha256=file_object.sha256,
                sha512=file_object.sha512,
                ssdeep=file_object.ssdeep,
            )
            file.save()
            log.success("Stored file details into database")

        storage = Storage()
        if not storage.get_file_path(projects.current.path, file_object.sha256):
            new_path = storage.add_file(projects.current.path, file_object)
            log.success("Stored file %s to %s", file_object.name, new_path)

    def run(self) -> None:
        try:
            super().run()
        except CommandRunError:
            return

        if not sessions.current:
            log.error("This command expects a session to a file to be open")
            return

        self.add_file(sessions.current.file)
