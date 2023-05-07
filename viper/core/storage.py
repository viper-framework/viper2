import logging
import os

from viper.common.file import FileObject

log = logging.getLogger("viper")


class Storage:
    def __init__(self) -> None:
        self.root_path = os.path.join(os.path.expanduser("~"), ".viper")
        self.projects_path = os.path.join(self.root_path, "projects")

    def add_file(self, project_path: str, file_object: FileObject) -> str:
        sha256 = file_object.sha256
        if not sha256:
            log.error("The file does not have a valid sha256 hash")
            return ""

        file_dir = os.path.join(
            project_path, "files", sha256[0], sha256[1], sha256[2], sha256[3]
        )

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        file_path = os.path.join(file_dir, sha256)

        if os.path.exists(file_path):
            log.warning("The file exists already, skip")
            return file_path

        with open(file_path, "wb") as handle:
            for chunk in file_object.get_chunks():
                handle.write(chunk)

        log.success("Successfully stored file in repository")
        return file_path

    def get_file_path(self, project_path: str, sha256: str) -> str:
        file_path = os.path.join(
            project_path, "files", sha256[0], sha256[1], sha256[2], sha256[3], sha256
        )

        if not os.path.exists(file_path):
            return ""

        return file_path
