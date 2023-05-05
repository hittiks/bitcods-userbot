from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.enums.chat_action import ChatAction
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".status": "<code>.status</code>  —  отправка моего статуса (например, \"печатает...\") в какой-то чат некоторое время\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди/юзернейм целевого чата для отправки\n"+
                        "    __**Второй параметр:**__ (обязательно) - целевой статус для отправки; варианты: \"typing\", \"upload_photo\", \"record_video\","+
                                " \"upload_video\", \"record_audio\", \"upload_audio\", \"upload_document\", \"find_location\", \"record_video_note\","+
                                " \"upload_video_note\", \"choose_contact\", \"playing\", \"speaking\", \"import_history\", \"choose_sticker\","+
                                " \"cancel\" - отменяет и убирает любой из вышеуказанных статусов"
}


# Отправка моего статуса (например, "печатает...") в какой-то чат некоторое время
async def status_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        target_chat = msg.text.split(" ", maxsplit=2)[1]
        target_status = msg.text.split(" ", maxsplit=2)[2]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Требуются параметры")
        return
    
    try:
        await cl.send_chat_action(target_chat, ChatAction[target_status.upper()])
    except (ValueError, KeyError):
        await send_temp_message(cl, msg.chat.id, "Неправильный параметр статуса")
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, "Неправильный параметр чата (PeerIdInvalid)")
    except exceptions.bad_request_400.UsernameInvalid:
        await send_temp_message(cl, msg.chat.id, "Неправильный параметр чата (UsernameInvalid)")


for a in apps:
    a.add_handler(MessageHandler(status_command_func, filters.command("status", prefixes=".") & filters.user("me")))
