import config
from enum import Enum
from pathlib import Path
from datetime import datetime
from termcolor import colored


class LogMode(Enum):
    OK = "green"
    INFO = "blue"
    TIME = "yellow"
    ERROR = "red"
    DEFAULT = "white"
    WARNING = "magenta"


def log(text: str, mode: LogMode) -> None:
    if config.LOG_TO_FILE:
        if not Path("../bitcods-userbot_logs").exists():
            Path("../userbot-logs").mkdir()

        with open(f"../bitcods-userbot_logs/log_{datetime.now().date()}.txt", "a", encoding="utf-8") as f:
            if config.LOGS_IS_COLORED:
                f.write(colored(text, color=mode.value) + "\n")
            else:
                f.write(text + "\n")
    else:
        if config.LOGS_IS_COLORED:
            print(colored(text, color=mode.value))
        else:
            print(text)
