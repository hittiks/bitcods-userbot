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
        ".hack": "<code>.hack</code>  —  команда \"взлома\" пентагона\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Команда "взлома" пентагона
async def hack_command_func(cl: Client, msg: Message):
    perc = 0

    while(perc < 100):
        if config.IS_STOP:
            return
        
        try:
            text = "👮‍ Взлом пентагона в процессе ..." + str(perc) + "%"
            await msg.edit(text)

            perc += random.randint(1, 3)
            await asyncio.sleep(0.1)

        except FloodWait as e:
            await asyncio.sleep(e.value)

    await msg.edit("🟢 Пентагон успешно взломан!")
    await asyncio.sleep(3)

    await msg.edit("👽 Поиск секретных данных об НЛО ...")
    perc = 0

    while(perc < 100):
        if config.IS_STOP:
            return
        
        try:
            text = "👽 Поиск секретных данных об НЛО ..." + str(perc) + "%"
            await msg.edit(text)

            perc += random.randint(1, 5)
            await asyncio.sleep(0.15)

        except FloodWait as e:
            await asyncio.sleep(e.value)

    await msg.edit("🦖 Найдены данные о существовании динозавров на земле!")


for a in apps:
    a.add_handler(MessageHandler(hack_command_func, filters.command("hack", prefixes=".") & filters.user("me")))
