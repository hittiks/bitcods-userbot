import os
import config
import mimetypes
mimetypes.init()
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".show": "<code>.show</code>  —  получение временного фото/видео в постоянное распоряжение (отправляется в чат Избранное)\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
    },
    "en": {
        ".show": "<code>.show</code>  —  getting a temporary photo/video as a permanent feature (sent to the chat Saved messages)\n"+
                "__**Required to send as a reply to the target message**__\n"+
                "==============================\n<u>Params</u>:\n    ~~Doesn't have~~"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_reply": "Команда должна быть ответом на сообщение",
        "unknown_media_type": "Тип медиа не распознан",
        "media_not_photo_or_video": "Медиа не является фото- или видеофайлом ('{0}')",
        "has_not_media": "Сообщение не содержит медиа для загрузки"
    },
    "en": {
        "require_reply": "The command must be a reply to a message",
        "unknown_media_type": "Media type not recognized",
        "media_not_photo_or_video": "Media is not photo or video file ('{0}')",
        "has_not_media": "Message has not media for loading"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def show_command_func(cl: Client, msg: Message):
    await msg.delete()

    if not msg.reply_to_message:
        await send_temp_message(cl, cl.me.id, get_phrase("require_reply"), 10)
        return
    
    try:
        path = await cl.download_media(msg.reply_to_message)
        mediatype = mimetypes.guess_type(path)[0]
        if not mediatype:
            await send_temp_message(cl, cl.me.id, get_phrase("unknown_media_type"), 10)
            return

        mt = mediatype.split("/")[0]
        if mt == "image":
            await cl.send_photo(cl.me.id, path)
            os.remove(path)
            os.removedirs("downloads")
        elif mt == "video":
            await cl.send_video(cl.me.id, path)
            os.remove(path)
            os.removedirs("downloads")
        else:
            await send_temp_message(cl, cl.me.id, get_phrase("media_not_photo_or_video").format(mediatype), 10)
            return
    except ValueError:
        await send_temp_message(cl, cl.me.id, get_phrase("has_not_media"), 10)
        return


for a in apps:
    a.add_handler(MessageHandler(show_command_func, filters.command("show", prefixes=".") & filters.user("me")))
