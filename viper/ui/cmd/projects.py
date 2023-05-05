import logging
import os
import time
from typing import Any

from viper.common.exceptions import ArgumentError
from viper.core.projects import projects

from .command import Command

log = logging.getLogger("viper")


class Projects(Command):
    cmd = "projects"
    description = "List or switch existing projects"

    def __init__(self):
        super(Projects, self).__init__()

        group = self.argparser.add_mutually_exclusive_group()
        group.add_argument(
            "-l", "--list", action="store_true", help="List all existing projects"
        )
        group.add_argument(
            "-s",
            "--switch",
            metavar="PROJECT NAME",
            help="Switch to the specified project (create one if it doesn't exist)",
        )
        group.add_argument(
            "-c",
            "--close",
            action="store_true",
            help="Close the currently open project",
        )
        group.add_argument(
            "-d",
            "--delete",
            metavar="PROJECT NAME",
            help="Delete the specified project",
        )

    def run(self, *args: Any):
        try:
            args = self.argparser.parse_args(args)
        except ArgumentError:
            return

        if args.list:
            projects_list = projects.list()
            if len(projects_list) == 0:
                log.info("There are no projects currently")
                return

            rows = []
            for project_path in projects_list:
                project_name = os.path.basename(project_path)
                project_ct_date = time.ctime(os.path.getctime(project_path))
                rows.append([project_name, project_ct_date])

            log.table({"columns": ["Project Name", "Creation Date"], "rows": rows})
            return

        if args.switch:
            projects.open(args.switch)
            log.success(f"Switched to project with name {args.switch}")
            return

        if args.close:
            projects.close()
            return

        log.error("You you didn't provide any action")
        self.argparser.print_usage()
