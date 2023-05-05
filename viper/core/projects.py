import logging
import os
from os.path import expanduser

log = logging.getLogger("viper")

PROJECT_DEFAULT = "default"

viper_root_path = os.path.join(expanduser("~"), ".viper")
viper_projects_path = os.path.join(viper_root_path, "projects")


# pylint: disable=too-few-public-methods
class Project:
    def __init__(self, name: str) -> None:
        self.name = name
        if self.name == PROJECT_DEFAULT:
            self.path = viper_root_path
        else:
            self.path = os.path.join(viper_projects_path, self.name)

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
        projects_list = []
        for project_name in os.listdir(viper_projects_path):
            projects_list.append(os.path.join(viper_projects_path, project_name))

        return projects_list


projects = Projects()
