import config
import asyncio
from utils import send_temp_message
from on_start import apps
from datetime import datetime

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".clock": "<code>.clock</code>  —  создаём сообщение-часы с периодическим обновлением\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - периодичность обновления (в секундах); например параметр 5 задаст обновление раз в 5 секунд"
}


# Создаём сообщение-часы с периодическим обновлением
async def clock_command_func(cl: Client, msg: Message):
    try:
        tick_time = int(msg.text.split(".clock ")[1])
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Требуется параметр в виде числа")
        return
    else:
        if tick_time <= 0:
            await send_temp_message(cl, msg.chat.id, "Число должно быть больше нуля")
            return

    while not config.IS_STOP:
        try:
            t = datetime.now()
            await msg.edit_text(str(t))
            await asyncio.sleep(tick_time)
        except:
            break


for a in apps:
    a.add_handler(MessageHandler(clock_command_func, filters.command("clock", prefixes=".") & filters.user("me")))
