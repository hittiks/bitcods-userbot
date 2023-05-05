import random
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".passgen": "<code>.passgen</code>  —  генератор паролей\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (необязательно) - количество знаков в пароле (8 по умолчанию)\n"+
                        "    __**Второй параметр:**__ (необязательно) - режим работы: 1 - только цифры; 2 - цифры и буквы; 3 - цифры, буквы и символы (1 по умолчанию)"
}


# Генератор паролей
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
        tbp="" # to be printed
        for _ in range(0, number):
            random.shuffle(symbols)
            tbp+=symbols[0]
        
        await cl.send_message(msg.chat.id, tbp, parse_mode=ParseMode.DISABLED)

    except Exception as e:
        log(f"----------'PASSGEN' HAVE GOT ERROR: {e}----------", LogMode.ERROR)


for a in apps:
    a.add_handler(MessageHandler(passgen_command_func, filters.command("passgen", prefixes=".") & filters.user("me")))
