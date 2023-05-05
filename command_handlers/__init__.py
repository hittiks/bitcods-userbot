import importlib
from pathlib import Path


def initialize_commands():
    for p in Path("command_handlers").absolute().iterdir():
        if not p.stem.startswith("__"):
            importlib.import_module("." + p.stem, __package__)
