import config
import asyncio
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import FloodWait
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".type": "<code>.type</code>  —  команда красивой печати (попробуй, чтобы понять)\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - текст для печати"
    },
    "en": {
        ".type": "<code>.type</code>  —  command for beautiful print (try it to understand)\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - text for print"
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


async def type_command_func(cl: Client, msg: Message):
    orig_text = msg.text.split(".type ", maxsplit=1)[1]
    text = orig_text
    tbp = "" # to be printed
    typing_symbol = "▒"

    while tbp != orig_text:
        if config.IS_STOP:
            return
        
        try:
            await msg.edit(tbp + typing_symbol)
            await asyncio.sleep(0.05) # 50 ms

            tbp = tbp + text[0]
            text = text[1:]

            await msg.edit(tbp)
            await asyncio.sleep(0.05)

        except FloodWait as e:
            await asyncio.sleep(e.value)


for a in apps:
    a.add_handler(MessageHandler(type_command_func, filters.command("type", prefixes=".") & filters.user("me")))
