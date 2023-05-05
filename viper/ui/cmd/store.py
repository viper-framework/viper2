import logging

from viper.common.file import FileObject
from viper.core.database import Database
from viper.core.sessions import sessions
from viper.core.storage import Storage

from .command import Command
from .projects import projects

log = logging.getLogger("viper")


class Store(Command):
    cmd = "store"
    description = "Store one or multiple files in the database and the local repository"

    def add_file(self, file_object: FileObject, tags=None) -> str | None:
        storage = Storage()
        if storage.get_file_path(projects.current.path, file_object.sha256):
            log.warning(f'Skip, file "{file_object.name}" appears to be already stored')
            return None

        status = Database().add(file_object=file_object, tags=tags)
        if not status:
            return None

        # If succeeds, store also in the local repository.
        # If something fails in the database (for example unicode strings)
        # we don't want to have the binary lying in the repository with no
        # associated database record.
        new_path = storage.add_file(projects.current.path, file_object)
        log.success(f'Stored file "{file_object.name}" to {new_path}')

        return new_path

    def run(self) -> None:
        super().run()

        if not sessions.current:
            log.error("This command expects a session to a file to be open")
            return

        new_path = self.add_file(sessions.current.file)
        sessions.new(new_path)