import os
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.file_id import FileId
from pyrogram.handlers import MessageHandler
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".getthumb": "<code>.getthumb</code>  —  получение \"заставки\" с видеосообщения (отправляется в тот же чат)\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Получение "заставки" с видеосообщения
async def getthumb_command_func(cl: Client, msg: Message):
    await msg.delete()

    if not msg.reply_to_message:
        await send_temp_message(cl, msg.chat.id, "Команда должна быть ответом на сообщение")
        return

    message = await cl.get_messages(msg.chat.id, msg.reply_to_message.id)
    
    if not message.media:
        await send_temp_message(cl, msg.chat.id, "Целевое сообщение не содержит медиа")
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
        await send_temp_message(cl, msg.chat.id, f"Данный тип медиа ({message.media}) не поддерживается")
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
