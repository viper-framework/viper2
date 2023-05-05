import argparse

from .shell import Shell


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="viper", description="Binary analysis and management framework"
    )
    parser.add_argument(
        "--modules",
        "-m",
        action="store",
        help="Path to a folder containing Viper modules to load",
    )
    args = parser.parse_args()

    shell = Shell()
    shell.run()
