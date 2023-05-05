import datetime
import logging
import time

from viper.common.file import File

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
        target_file = File(file_path)
        for session in self.__sessions:
            if session.file and session.file.path == session.file.path:
                log.error(
                    f"There is already a session open with file to path {session.file.path}"
                )
                return

        session = Session()
        session.id = len(self.__sessions) + 1
        session.file = target_file

        self.__sessions.append(session)
        self.current = session

        log.success(
            f"New session opened to file {session.file.path} with ID {session.id}"
        )


sessions = Sessions()
