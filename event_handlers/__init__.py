import importlib
from pathlib import Path


def initialize_filters():
    for p in Path("event_handlers").absolute().iterdir():
        if not p.stem.startswith("__"):
            importlib.import_module("." + p.stem, __package__)
