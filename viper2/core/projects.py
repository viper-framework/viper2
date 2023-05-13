import logging
import os

from .storage import Storage

log = logging.getLogger("viper")

PROJECT_DEFAULT = "default"


# pylint: disable=too-few-public-methods
class Project:
    def __init__(self, name: str) -> None:
        self.name = name
        if self.name == PROJECT_DEFAULT:
            self.path = Storage().root_path
        else:
            self.path = os.path.join(Storage().projects_path, self.name)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def is_default(self) -> bool:
        if self.name == PROJECT_DEFAULT:
            return True

        return False


class Projects:
    def __init__(self) -> None:
        self.current = Project(PROJECT_DEFAULT)

    def open(self, name: str) -> None:
        self.current = Project(name)

    def close(self) -> None:
        if self.current and self.current.name != PROJECT_DEFAULT:
            self.current = Project(PROJECT_DEFAULT)

    def list(self) -> list:
        if not os.path.exists(Storage().projects_path):
            return []

        projects_list = []
        for project_name in os.listdir(Storage().projects_path):
            projects_list.append(os.path.join(Storage().projects_path, project_name))

        return projects_list


projects = Projects()
