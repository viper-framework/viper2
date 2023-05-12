import argparse
import logging
import shlex

from ..core.modules import load_modules, modules
from ..core.projects import projects
from ..core.sessions import sessions
from .logger import init_logging
from .shell import Shell

init_logging()

log = logging.getLogger("viper")


def run(cmd: str, modules_path: str) -> None:
    load_modules(modules_path)
    cmd_words = shlex.split(cmd)
    cmd_name = cmd_words[0].lower().strip()
    cmd_args = cmd_words[1:]

    if cmd_name in modules:
        mod = modules[cmd_name]["class"]()
        mod.add_args(*cmd_args)
        mod.run()
    else:
        log.error('No module found for "%s"', cmd_name)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="viper", description="Binary analysis and management framework"
    )
    parser.add_argument(
        "-m",
        "--modules",
        action="store",
        metavar="MODULES_PATH",
        help="path to a folder containing Viper modules to load",
    )
    parser.add_argument(
        "-p",
        "--project",
        action="store",
        metavar="PROJECT_NAME",
        help="open a project",
    )
    parser.add_argument(
        "-o",
        "--open",
        action="store",
        metavar="FILE_PATH",
        help="open a file",
    )
    parser.add_argument(
        "-r",
        "--run",
        action="store",
        metavar="COMMAND",
        help="run a command or module instead of opening the shell",
    )
    args = parser.parse_args()

    if args.project:
        projects.open(args.project)

    if args.open:
        sessions.new(args.open)

    if args.run:
        run(cmd=args.run, modules_path=args.modules)
        return

    shell = Shell(modules_path=args.modules)
    shell.run()
