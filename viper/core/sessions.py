import datetime
import logging
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

        session = Session()
        session.id = len(self.__sessions) + 1
        session.file = file_object

        self.__sessions.append(session)
        self.current = session

        log.success(
            "New session opened to file %s with ID %d", session.file.path, session.id
        )


sessions = Sessions()
