import logging
import os
from os.path import expanduser

log = logging.getLogger("viper")

project_default = "default"
viper_root_path = os.path.join(expanduser("~"), ".viper")
viper_projects_path = os.path.join(viper_root_path, "projects")


class Project:
    def __init__(self, name: str):
        self.name = name
        if self.name == project_default:
            self.path = viper_root_path
        else:
            self.path = os.path.join(viper_projects_path, self.name)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def is_default(self) -> bool:
        if self.name == project_default:
            return True

        return False


class Projects:
    def __init__(self):
        self.current = Project(project_default)

    def open(self, name: str):
        self.current = Project(name)

    def close(self):
        if self.current and self.current.name != project_default:
            self.current = Project(project_default)

    def list(self) -> list:
        projects_list = []
        for project_name in os.listdir(viper_projects_path):
            projects_list.append(os.path.join(viper_projects_path, project_name))

        return projects_list


projects = Projects()