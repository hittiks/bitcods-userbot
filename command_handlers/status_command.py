import config
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.enums.chat_action import ChatAction
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".status": "<code>.status</code>  —  отправка моего статуса (например, \"печатает...\") в какой-то чат некоторое время\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди/юзернейм целевого чата для отправки\n"+
                        "    __**Второй параметр:**__ (обязательно) - целевой статус для отправки; варианты: \"typing\", \"upload_photo\", \"record_video\","+
                                " \"upload_video\", \"record_audio\", \"upload_audio\", \"upload_document\", \"find_location\", \"record_video_note\","+
                                " \"upload_video_note\", \"choose_contact\", \"playing\", \"speaking\", \"import_history\", \"choose_sticker\","+
                                " \"cancel\" - отменяет и убирает любой из вышеуказанных статусов"
    },
    "en": {
        ".status": "<code>.status</code>  —  sending my status (e.g. \"typing...\") to some chat for a while\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - id/username of target chat to sending\n"+
                        "    __**Second param:**__ (required) - target status for sending; variants: \"typing\", \"upload_photo\", \"record_video\","+
                                " \"upload_video\", \"record_audio\", \"upload_audio\", \"upload_document\", \"find_location\", \"record_video_note\","+
                                " \"upload_video_note\", \"choose_contact\", \"playing\", \"speaking\", \"import_history\", \"choose_sticker\","+
                                " \"cancel\" - cancels and removes any of the above statuses"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_params": "Требуются параметры",
        "incorect_status_param": "Неправильный параметр статуса",
        "incorect_chat_param": "Неправильный параметр чата ({0})"
    },
    "en": {
        "require_params": "Require params",
        "incorect_status_param": "Incorect status param",
        "incorect_chat_param": "Incorect chat param ({0})"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def status_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        target_chat = msg.text.split(" ", maxsplit=2)[1]
        target_status = msg.text.split(" ", maxsplit=2)[2]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_params"))
        return
    
    try:
        await cl.send_chat_action(target_chat, ChatAction[target_status.upper()])
    except (ValueError, KeyError):
        await send_temp_message(cl, msg.chat.id, get_phrase("incorect_status_param"))
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorect_chat_param").format("PeerIdInvalid"))
    except exceptions.bad_request_400.UsernameInvalid:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorect_chat_param").format("UsernameInvalid"))


for a in apps:
    a.add_handler(MessageHandler(status_command_func, filters.command("status", prefixes=".") & filters.user("me")))
