import datetime
import os
import time
from typing import List, Optional

from viper2 import printer

from ..common.file import FileObject
from .database import File


# pylint: disable=too-few-public-methods
class Session:
    def __init__(self) -> None:
        self.identifier: int
        self.file: FileObject
        self.created_at = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


class Sessions:
    def __init__(self) -> None:
        self.current: Optional[Session] = None
        self.__sessions: List[Session] = []

        # This is used to keep trace of the results from the last "find" command
        # so we can reference them in other commands (primarily "open").
        # TODO: However, this is not really the optimal place for this, as
        #       this class is intended only to keep track of currently open
        #       files. Find results are a little off-spec.
        self.__last_find: List[File] = []

    def add_find(self, results: List[File]) -> None:
        self.__last_find = results

    def get_find(self) -> List[File]:
        return self.__last_find

    def all(self) -> List[Session]:
        return self.__sessions

    def close(self) -> None:
        self.current = None

    def reset(self) -> None:
        self.close()
        self.__sessions = []

    def switch(self, session: Session) -> None:
        self.current = session

    def new(self, file_path: str) -> None:
        file_object = FileObject(file_path)
        for session in self.__sessions:
            if session.file and session.file.path == file_path:
                printer.error(
                    "There is already a session open with file to path %s",
                    session.file.path,
                )
                return

        if not os.path.exists(file_object.path):
            printer.error("File does not exist at path %s", file_object.path)
            return

        session = Session()
        session.identifier = len(self.__sessions) + 1
        session.file = file_object

        try:
            file = File.get(File.sha256 == file_object.sha256)
        except File.DoesNotExist:  # pylint: disable=no-member
            pass
        else:
            session.file.name = file.name

        self.__sessions.append(session)
        self.current = session

        printer.success(
            "New session opened to file %s with ID %d",
            session.file.path,
            session.identifier,
        )


sessions = Sessions()
