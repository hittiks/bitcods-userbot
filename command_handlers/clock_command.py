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
    "ru": {
        ".clock": "<code>.clock</code>  —  создаём сообщение-часы с периодическим обновлением\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - периодичность обновления (в секундах); например параметр 5 задаст обновление раз в 5 секунд"
    },
    "en": {
        ".clock": "<code>.clock</code>  —  create clock-message with periodically updating\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - period of updating (in seconds); for example param 5 set updating every 5 second"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_param_as_num": "Требуется параметр в виде числа",
        "num_greater_than_null": "Число должно быть больше нуля"
    },
    "en": {
        "require_param_as_num": "Require param as a num",
        "num_greater_than_null": "Num must be greater than null"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def clock_command_func(cl: Client, msg: Message):
    try:
        tick_time = int(msg.text.split(".clock ")[1])
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_param_as_num"))
        return
    else:
        if tick_time <= 0:
            await send_temp_message(cl, msg.chat.id, get_phrase("num_greater_than_null"))
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
