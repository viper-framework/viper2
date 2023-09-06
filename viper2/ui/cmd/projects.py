# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os
import shutil
import time

from prompt_toolkit.shortcuts import confirm

from viper2 import printer
from viper2.core.projects import projects
from viper2.core.sessions import sessions

from .command import Command, CommandRunError


class Projects(Command):
    cmd = "projects"
    description = "List or switch existing projects"

    def __init__(self) -> None:
        super().__init__()

        group = self.args_parser.add_mutually_exclusive_group()
        group.add_argument(
            "-l", "--list", action="store_true", help="list all existing projects"
        )
        group.add_argument(
            "-s",
            "--switch",
            metavar="PROJECT NAME",
            help="switch to the specified project (create one if it doesn't exist)",
        )
        group.add_argument(
            "-c",
            "--close",
            action="store_true",
            help="close the currently open project",
        )
        group.add_argument(
            "-d",
            "--delete",
            metavar="PROJECT NAME",
            help="delete the specified project",
        )

    def run(self) -> None:
        try:
            super().run()
        except CommandRunError:
            return

        if self.args.list:
            projects_list = projects.list()
            if len(projects_list) == 0:
                printer.info("There are no projects currently")
                return

            rows = []
            for project_path in projects_list:
                project_name = os.path.basename(project_path)
                project_ct_date = time.ctime(os.path.getctime(project_path))
                rows.append([project_name, project_ct_date])

            printer.table(columns=["Project Name", "Creation Date"], rows=rows)
        elif self.args.switch:
            # When we switch project, we reset sessions so that any previously
            # open sessions are closed and removed.
            sessions.reset()
            projects.open(self.args.switch)
            printer.success('Switched to project with name "%s"', self.args.switch)
        elif self.args.close:
            # Similarly to switch, if we close the current project, we should
            # also close all active sessions.
            sessions.reset()
            projects.close()
        elif self.args.delete:
            delete = confirm(
                "Are you sure? This will permanently delete all files in that project!"
            )
            if not delete:
                return

            if projects.current.name == self.args.delete:
                projects.close()

            for project_path in projects.list():
                if os.path.basename(project_path) == self.args.delete:
                    shutil.rmtree(project_path)
                    printer.success(
                        "Successfully deleted project at path %s", project_path
                    )
                    return

            printer.error('Could not find a project with name "%s"', self.args.delete)
        else:
            self.args_parser.print_usage()
