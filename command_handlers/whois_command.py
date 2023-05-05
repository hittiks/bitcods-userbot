import os
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".whois": "<code>.whois</code>  —  получение данных о пользователе/чате по его айди/номере телефона или юзернейму\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди/номер телефона/юзернейм целевого пользователя/чата"
}


# Получение данных о пользователе/чате по его айди/номере телефона или юзернейму
async def whois_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        id = msg.text.split(maxsplit=1)[1]
        if "+" not in id and id.isdigit():
            id = int(id)
    except:
        await send_temp_message(cl, msg.chat.id, "Требуется параметр")
        return
    
    try:
        user = await cl.get_users(id)
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, "Получена ошибка PeerIdInvalid при попытке получить пользователя")
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Получена ошибка IndexError (скорее всего нет такого пользователя)")
    else:
        log(str(user), LogMode.INFO)
        try:
            await cl.send_message(msg.chat.id, str(user))
        except exceptions.bad_request_400.MessageTooLong:
            log("----------MESSAGE TOO LONG----------", LogMode.ERROR)
            await send_temp_message(cl, msg.chat.id, "Сообщение слишком большое")
            with open("user.txt", "w", encoding="utf-8") as f:
                f.write(str(chat))
            await cl.send_document(msg.chat.id, "user.txt")
            try:
                os.remove("user.txt")
            except FileNotFoundError:
                pass

    try:
        chat = await cl.get_chat(id)
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, "Получена ошибка PeerIdInvalid при попытке получить чат")
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Получена ошибка IndexError (скорее всего нет такого чата)")
    else:
        log(str(chat), LogMode.INFO)
        try:
            await cl.send_message(msg.chat.id, str(chat))
        except exceptions.bad_request_400.MessageTooLong:
            log("----------MESSAGE TOO LONG----------", LogMode.ERROR)
            await send_temp_message(cl, msg.chat.id, "Сообщение слишком большое")
            with open("chat.txt", "w", encoding="utf-8") as f:
                f.write(str(chat))
            await cl.send_document(msg.chat.id, "chat.txt")
            try:
                os.remove("chat.txt")
            except FileNotFoundError:
                pass


for a in apps:
    a.add_handler(MessageHandler(whois_command_func, filters.command("whois", prefixes=".") & filters.user("me")))
