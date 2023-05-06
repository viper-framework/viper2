import importlib
import inspect
import logging
import os
import pkgutil
import sys

from viper.common.module import Module

log = logging.getLogger("viper")
modules = {}


def load_modules(modules_path: str) -> None:
    if not modules_path:
        return

    if not os.path.exists(modules_path):
        log.error("The modules directory does not exist at path: %s", modules_path)
        return

    global modules
    sys.path.insert(0, modules_path)
    for _, module_name, ispkg in pkgutil.iter_modules([modules_path]):
        if ispkg:
            continue

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            log.error('Failed to import module with name "%s": %s', module_name, exc)
            continue

        for member_name, member_object in inspect.getmembers(module):
            if not inspect.isclass(member_object):
                continue

            if issubclass(member_object, Module) and member_object is not Module:
                if not hasattr(member_object, "cmd"):
                    log.error(
                        "The module %s does not have a `cmd` attribute, cannot load",
                        member_name,
                    )
                    continue

                log.debug(
                    "Loaded module %s (%s)",
                    member_object.cmd,
                    member_object.description,
                )
                modules[member_object.cmd] = {
                    "class": member_object,
                    "description": member_object.description,
                }

    sys.path.remove(modules_path)
