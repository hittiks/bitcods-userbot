import config
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".stop": "<code>.stop</code>  —  команда остановки этой программы\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
    },
    "en": {
        ".stop": "<code>.stop</code>  —  command to stop this program\n"+
                "==============================\n<u>Params</u>:\n    ~~Doesn't have~~"
    }
}


PHRASES_VAR = {
    "ru": {
        "<empty>": "<empty>"
    },
    "en": {
        "<empty>": "<empty>"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def stop_command_func(cl: Client, msg: Message):
    await msg.delete()
    config.IS_STOP = True
    
    log(f"----------EXIT FROM USERBOT WITH COMMAND BY USER REQUIRE----------", LogMode.OK)

    for a in apps:
        await a.stop(block=False)
    
    log("----------USERBOT STOPED CORRECTLY BY COMMAND----------", LogMode.OK)
    exit(0)


for a in apps:
    a.add_handler(MessageHandler(stop_command_func, filters.command("stop", prefixes=".") & filters.user("me")))
