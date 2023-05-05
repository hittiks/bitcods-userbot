import os
import mimetypes
mimetypes.init()
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".show": "<code>.show</code>  —  получение временной фотки/видоса в постоянное распоряжение (отправляется в тот же чат)\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Получение временной фотки/видоса в постоянное распоряжение
async def show_command_func(cl: Client, msg: Message):
    await msg.delete()

    if not msg.reply_to_message:
        await send_temp_message(cl, msg.chat.id, "Команда должна быть ответом на сообщение")
        return
    
    try:
        path = await cl.download_media(msg.reply_to_message)
        mediatype = mimetypes.guess_type(path)[0]
        if not mediatype:
            await send_temp_message(cl, msg.chat.id, "Тип медиа не распознан")
            return

        mt = mediatype.split("/")[0]
        if mt == "image":
            await cl.send_photo(msg.chat.id, path)
            os.remove(path)
            os.removedirs("downloads")
        elif mt == "video":
            await cl.send_video(msg.chat.id, path)
            os.remove(path)
            os.removedirs("downloads")
        else:
            await send_temp_message(cl, msg.chat.id, f"Медиа не является фото- или видеофайлом ('{mediatype}')")
            return
    except ValueError:
        await send_temp_message(cl, msg.chat.id, "Сообщение не содержит медиа для загрузки")
        return


for a in apps:
    a.add_handler(MessageHandler(show_command_func, filters.command("show", prefixes=".") & filters.user("me")))
