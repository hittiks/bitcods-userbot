import config
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".stop": "<code>.stop</code>  —  команда остановки этого скрипта\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Команда остановки скрипта
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
