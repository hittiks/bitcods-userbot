import random
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
        ".hack": "<code>.hack</code>  —  команда \"взлома\" пентагона\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
    },
    "en": {
        ".hack": "<code>.hack</code>  —  command to \"hack\" pentagon\n"+
                "==============================\n<u>Params</u>:\n    ~~Doesn't have~~"
    }
}


PHRASES_VAR = {
    "ru": {
        "hack_in_process": "👮‍ Взлом пентагона в процессе ...",
        "successfully_hacked": "🟢 Пентагон успешно взломан!",
        "find_in_process": "👽 Поиск секретных данных об НЛО ...",
        "successfully_finded": "🦖 Найдены данные о существовании динозавров на земле!"
    },
    "en": {
        "hack_in_process": "👮‍ Hacking pentagon in process ...",
        "successfully_hacked": "🟢 Pentagon successfully hacked!",
        "find_in_process": "👽 Finding secret info about UFO ...",
        "successfully_finded": "🦖 Finded info about the existence of dinosaurs on earth!"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def hack_command_func(cl: Client, msg: Message):
    perc = 0

    while(perc < 100):
        if config.IS_STOP:
            return
        
        try:
            text = get_phrase("hack_in_process") + str(perc) + "%"
            await msg.edit(text)

            perc += random.randint(1, 3)
            await asyncio.sleep(0.1)

        except FloodWait as e:
            await asyncio.sleep(e.value)

    await msg.edit(get_phrase("successfully_hacked"))
    await asyncio.sleep(3)

    await msg.edit(get_phrase("find_in_process"))
    perc = 0

    while(perc < 100):
        if config.IS_STOP:
            return
        
        try:
            text = get_phrase("find_in_process") + str(perc) + "%"
            await msg.edit(text)

            perc += random.randint(1, 5)
            await asyncio.sleep(0.15)

        except FloodWait as e:
            await asyncio.sleep(e.value)

    await msg.edit(get_phrase("successfully_finded"))


for a in apps:
    a.add_handler(MessageHandler(hack_command_func, filters.command("hack", prefixes=".") & filters.user("me")))
