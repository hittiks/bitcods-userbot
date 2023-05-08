import random
import config
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".passgen": "<code>.passgen</code>  —  генератор паролей\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (необязательно) - количество знаков в пароле, она же длинна (8 по умолчанию)\n"+
                        "    __**Второй параметр:**__ (необязательно) - режим работы: 1 - только цифры, 2 - цифры и буквы,"+
                                " 3 - цифры, буквы и специальные символы (1 по умолчанию)"
    },
    "en": {
        ".passgen": "<code>.passgen</code>  —  passwords generator\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (not required) - num of symbols in password also known as length (8 by default)\n"+
                        "    __**Second param:**__ (not required) - working mode: 1 - only numbers, 2 - numbers and letters,"+
                                " 3 - numbers, letters and special symbols (1 by default)"
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


async def passgen_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        number = int(msg.text.split(maxsplit=2)[1])
    except IndexError or ValueError:
        number = 8
    
    try:
        work_mode = int(msg.text.split(maxsplit=2)[2])
    except IndexError or ValueError:
        work_mode = 1
    
    alph = {
        1: "1234567890",
        2: "1234567890abcdefghijklmnopqrstuvwxyz",
        3: "1234567890abcdefghijklmnopqrstuvwxyz!@#№$;%:^&?+-*/.,[](){|}\\`~_=<>'\"",
    }
    
    try:
        symbols = list(alph[work_mode])
    except KeyError:
        symbols = list(alph[1])

    try:
        password=""
        for _ in range(0, number):
            random.shuffle(symbols)
            password += symbols[0]
        
        await cl.send_message(msg.chat.id, password, parse_mode=ParseMode.DISABLED)

    except Exception as e:
        log(f"----------'PASSGEN' HAVE GOT ERROR: {e}----------", LogMode.ERROR)


for a in apps:
    a.add_handler(MessageHandler(passgen_command_func, filters.command("passgen", prefixes=".") & filters.user("me")))
