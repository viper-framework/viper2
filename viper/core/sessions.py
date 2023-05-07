import datetime
import logging
import os
import time

from viper.common.file import FileObject

log = logging.getLogger("viper")


# pylint: disable=too-few-public-methods
class Session:
    def __init__(self) -> None:
        self.id = None  # pylint: disable=invalid-name
        self.file = None
        self.created_at = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


class Sessions:
    def __init__(self) -> None:
        self.current = None
        self.__sessions = []

        # This is used to keep trace of the results from the last "find" command
        # so we can reference them in other commands (primarily "open").
        # TODO: However, this is not really the optimal place for this, as
        #       this class is intended only to keep track of currently open
        #       files. Find results are a little off-spec.
        self.__last_find = []

    def add_find(self, results: list) -> None:
        self.__last_find = results

    def get_find(self) -> list:
        return self.__last_find

    def list(self) -> list:
        return self.__sessions

    def close(self) -> None:
        self.current = None

    def switch(self, session: Session) -> None:
        self.current = session

    def new(self, file_path: str) -> None:
        file_object = FileObject(file_path)
        for session in self.__sessions:
            if session.file and session.file.path == file_path:
                log.error(
                    "There is already a session open with file to path %s",
                    session.file.path,
                )
                return

        if not os.path.exists(file_object.path):
            log.error("File does not exist at path %s", file_object.path)
            return

        session = Session()
        session.id = len(self.__sessions) + 1
        session.file = file_object

        self.__sessions.append(session)
        self.current = session

        log.success(
            "New session opened to file %s with ID %d", session.file.path, session.id
        )


sessions = Sessions()
