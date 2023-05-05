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
        ".findpidor": "<code>.findpidor</code>  —  команда \"поиска\" пидора, любимой и подобных\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Команда "поиска" пидора, любимой и подобных
async def findpidor_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    perc = 0
    num_of_dot = 1
    texts = [
        "Поиск пидора в процессе|Пидор обнаружен!",
        "Поиск конча в процессе|Конч обнаружен!",
        "Поиск лапочки в процессе|Лапочка обнаружена!",
        "Поиск любимой в процессе|Любимая обнаружена!",
        "Поиск зайки в процессе|Зайка обнаружена!",
        "Поиск киси в процессе|Кися обнаружена!",
        "Поиск гандона в процессе|Гандон обнаружен!",
        "Поиск дауна в процессе|Даун обнаружен!",
        "Поиск долбоёба в процессе|Долбоёб обнаружен!",
        "Поиск клоуна в процессе|Клоун обнаружен!",
    ]
    phrases = texts[random.randint(0, len(texts)-1)].split("|")

    mess = await cl.send_message(msg.chat.id, ".")
    while(perc < 100):
        if config.IS_STOP:
            return
        
        try:
            text = phrases[0] + "."*num_of_dot + "\n" + "| "*int(perc/10) + "\n" + str(perc) + "%"
            await mess.edit(text)
            num_of_dot+=1
            if num_of_dot>3:
                num_of_dot = 1

            perc += random.randint(7, 19)
            await asyncio.sleep(0.1)

        except FloodWait as e:
            await asyncio.sleep(e.value)

    await mess.edit(phrases[1])


for a in apps:
    a.add_handler(MessageHandler(findpidor_command_func, filters.command("findpidor", prefixes=".") & filters.user("me")))
