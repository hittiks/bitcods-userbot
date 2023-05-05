import config
import random
import asyncio
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import FloodWait
from pyrogram.handlers import MessageHandler
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".decrypt": "<code>.decrypt</code>  —  типа type 2.0, имитация расшифровки сообщения\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевой текст для имитации его расшифровки"
}


# Типа type 2.0, имитация расшифровки сообщения
async def decrypt_command_func(cl: Client, msg: Message):
    await msg.delete()

    try:
        target_text = msg.text.split(".decrypt ")[1]
        if not target_text:
            raise ValueError
    except:
        await send_temp_message(cl, msg.chat.id, "Требуется параметр в виде целевого текста")
        return

    target_symbols = list(target_text)
    target_indexes = [x for x in range(len(target_text))]
    
    text_now = "".join(chr(random.randint(0, 1000)) for _ in range(len(target_text)))

    perc = 0
    num_of_dot = 1
    counter = 0

    mess = await cl.send_message(msg.chat.id, "Начинаю расшифровку послания...")
    await asyncio.sleep(2)
    while(perc < 100):
        if config.IS_STOP:
            return
        
        counter += 1
        try:
            for _ in range(5):
                if len(target_indexes) == 0:
                    perc = 100
                    break
                ind = target_indexes.pop(random.randint(0, len(target_indexes)-1))
                text_now = text_now[:ind] + target_symbols[ind] + text_now[ind+1:]


            text = "Расшифровка в процессе" + "."*num_of_dot + "\n" + "| "*int(perc/10) + "\n" + str(perc) + "%\n" + text_now
            await mess.edit_text(text, ParseMode.DISABLED)
            num_of_dot+=1
            if num_of_dot>3:
                num_of_dot = 1

            perc = int(counter * 5 / len(target_text) * 100)
            await asyncio.sleep(1)

        except FloodWait as e:
            await asyncio.sleep(e.value)

    await mess.edit_text(target_text)


for a in apps:
    a.add_handler(MessageHandler(decrypt_command_func, filters.command("decrypt", prefixes=".") & filters.user("me")))
