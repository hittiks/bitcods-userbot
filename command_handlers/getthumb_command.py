import os
import config
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.file_id import FileId
from pyrogram.handlers import MessageHandler
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".getthumb": "<code>.getthumb</code>  —  получение \"заставки\" с видео, гиф или видеосообщения (отправляется в тот же чат)\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
    },
    "en": {
        ".getthumb": "<code>.getthumb</code>  —  getting \"thumb\" from video, gif or video note (sends in current chat)\n"+
                "__**Required to send as a reply to the target message**__\n"+
                "==============================\n<u>Params</u>:\n    ~~Doesn't have~~"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_reply": "Команда должна быть ответом на сообщение",
        "not_media": "Целевое сообщение не содержит медиа",
        "not_supported": "Данный тип медиа ({0}) не поддерживается"
    },
    "en": {
        "require_reply": "Require a reply to target message",
        "not_media": "Target message has not media",
        "not_supported": "This type of media ({0}) is not supported"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def getthumb_command_func(cl: Client, msg: Message):
    await msg.delete()

    if not msg.reply_to_message:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_reply"))
        return

    message = await cl.get_messages(msg.chat.id, msg.reply_to_message.id)
    
    if not message.media:
        await send_temp_message(cl, msg.chat.id, get_phrase("not_media"))
        return

    if message.media == MessageMediaType.VIDEO:
        file_id = message.video.thumbs[0].file_id
        file_size = message.video.thumbs[0].file_size
    elif message.media == MessageMediaType.ANIMATION:
        file_id = message.animation.thumbs[0].file_id
        file_size = message.animation.thumbs[0].file_size
    elif message.media == MessageMediaType.VIDEO_NOTE:
        file_id = message.video_note.thumbs[0].file_id
        file_size = message.video_note.thumbs[0].file_size
    else:
        await send_temp_message(cl, msg.chat.id, get_phrase("not_supported").format(message.media))
        return

    thumb_path = str(await cl.handle_download((FileId.decode(file_id), "./downloads/", file_id + ".jpg", False, file_size, None, ())))
    await cl.send_photo(msg.chat.id, thumb_path)

    try:
        os.remove(thumb_path)
    except FileNotFoundError:
        pass

    try:
        os.removedirs("downloads")
    except FileNotFoundError:
        pass


for a in apps:
    a.add_handler(MessageHandler(getthumb_command_func, filters.command("getthumb", prefixes=".") & filters.user("me")))
