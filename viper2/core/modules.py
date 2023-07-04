import importlib
import inspect
import logging
import os
import pkgutil
import shutil
import sys
import tempfile

from pipreqs import pipreqs # type: ignore

from ..common.module import Module

log = logging.getLogger("viper")
modules = {}


def get_module_dependencies(module_path: str) -> list:
    if not os.path.exists(module_path):
        return []

    imports = []
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(module_path, os.path.join(temp_dir, os.path.basename(module_path)))
        imports = pipreqs.get_all_imports(temp_dir)

    return imports


def have_dependency(dependency: str) -> bool:
    if dependency == "viper":
        return True

    try:
        importlib.import_module(dependency)
    except ModuleNotFoundError:
        return False

    return True


def load_modules(modules_path: str) -> None:
    if not modules_path:
        return

    if not os.path.exists(modules_path):
        log.error("The modules directory does not exist at path: %s", modules_path)
        return

    sys.path.insert(0, modules_path)
    for _, module_name, ispkg in pkgutil.iter_modules([modules_path]):
        if ispkg:
            continue

        module_path = os.path.join(modules_path, f"{module_name}.py")
        dependencies = get_module_dependencies(module_path)
        can_import = True
        for dep in dependencies:
            if not have_dependency(dep):
                can_import = False
                log.error(
                    "Module at path %s requires the following missing library: '%s'",
                    module_path,
                    dep,
                )

        if not can_import:
            log.error("Cannot proceed importing module '%s'", module_name)
            continue

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            log.error("Failed to import module with name '%s': %s", module_name, exc)
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
