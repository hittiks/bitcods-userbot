import os
import config
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".whois": "<code>.whois</code>  —  получение данных о пользователе/чате по его айди, номере телефона или юзернейму\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди, номер телефона или юзернейм целевого пользователя/чата"
    },
    "en": {
        ".whois": "<code>.whois</code>  —  getting data about user/chat by him id, phone number or username\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - id, phone number or username of target user/chat"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_param": "Требуется параметр",
        "get_error_peer_id_invalid_for_user": "Получена ошибка PeerIdInvalid при попытке получить пользователя",
        "get_error_index_error_for_user": "Получена ошибка IndexError (скорее всего нет такого пользователя)",
        "message_too_long": "Сообщение слишком большое",
        "get_error_peer_id_invalid_for_chat": "Получена ошибка PeerIdInvalid при попытке получить чат",
        "get_error_index_error_for_chat": "Получена ошибка IndexError (скорее всего нет такого чата)"
    },
    "en": {
        "require_param": "Require param",
        "get_error_peer_id_invalid_for_user": "Get error PeerIdInvalid when trying to get a user",
        "get_error_index_error_for_user": "Get error IndexError (most likely no such user)",
        "message_too_long": "Message too long",
        "get_error_peer_id_invalid_for_chat": "Get error PeerIdInvalid when trying to get a chat",
        "get_error_index_error_for_chat": "Get error IndexError (most likely no such chat)"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def whois_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        id = msg.text.split(maxsplit=1)[1]
        if "+" not in id and id.isdigit():
            id = int(id)
    except:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_param"))
        return
    
    try:
        user = await cl.get_users(id)
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, get_phrase("get_error_peer_id_invalid_for_user"))
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("get_error_index_error_for_user"))
    else:
        log(str(user), LogMode.INFO)
        try:
            await cl.send_message(msg.chat.id, str(user))
        except exceptions.bad_request_400.MessageTooLong:
            log("----------MESSAGE TOO LONG----------", LogMode.ERROR)
            await send_temp_message(cl, msg.chat.id, get_phrase("message_too_long"))
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
        await send_temp_message(cl, msg.chat.id, get_phrase("get_error_peer_id_invalid_for_chat"))
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("get_error_index_error_for_chat"))
    else:
        log(str(chat), LogMode.INFO)
        try:
            await cl.send_message(msg.chat.id, str(chat))
        except exceptions.bad_request_400.MessageTooLong:
            log("----------MESSAGE TOO LONG----------", LogMode.ERROR)
            await send_temp_message(cl, msg.chat.id, get_phrase("message_too_long"))
            with open("chat.txt", "w", encoding="utf-8") as f:
                f.write(str(chat))
            await cl.send_document(msg.chat.id, "chat.txt")
            try:
                os.remove("chat.txt")
            except FileNotFoundError:
                pass


for a in apps:
    a.add_handler(MessageHandler(whois_command_func, filters.command("whois", prefixes=".") & filters.user("me")))
