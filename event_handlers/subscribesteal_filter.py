import os
import config
import sqlite3
from pathlib import Path
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.file_id import FileId
from pyrogram.handlers import MessageHandler
from pyrogram.enums.chat_type import ChatType
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.types.user_and_chats.chat import Chat
from pyrogram.types.messages_and_media.message import Message


async def __download_progress(current: int, total: int, msg: Message):
    if msg.text:
        await msg.edit_text(f"Загрузка: {int(current/total*100)} %")


async def __upload_progress(current: int, total: int, msg: Message):
    if msg.text:
        await msg.edit_text(f"Отправка: {int(current/total*100)} %")


async def __send_media(cl: Client, msg: Message, mess: Message):
    try:
        path = await cl.download_media(mess, progress=__download_progress, progress_args=(msg,))
    except ValueError:
        if mess.service:
            pass
        elif mess.text:
            return await cl.send_message(msg.chat.id, mess.text)
        else:
            log(f"----------SEND MEDIA FUNCTION GET UNKNOWN ERROR WITH MESSAGE: '{mess}'----------", LogMode.INFO)
        return
        
    log(str(path), LogMode.INFO)

    caption = mess.caption or ""
    if mess.media == MessageMediaType.PHOTO:
        return await cl.send_photo(msg.chat.id, path, caption=caption, progress=__upload_progress, progress_args=(msg,))
    elif mess.media == MessageMediaType.VIDEO:
        thumb = str(await cl.handle_download((FileId.decode(mess.video.thumbs[0].file_id), "./downloads/", mess.video.thumbs[0].file_id + ".jpg", False, mess.video.thumbs[0].file_size, None, ())))
        return await cl.send_video(msg.chat.id, path, caption=caption, duration=mess.video.duration, width=mess.video.width, height=mess.video.height, thumb=thumb, progress=__upload_progress, progress_args=(msg,))
    elif mess.media == MessageMediaType.ANIMATION:
        thumb = str(await cl.handle_download((FileId.decode(mess.animation.thumbs[0].file_id), "./downloads/", mess.animation.thumbs[0].file_id + ".jpg", False, mess.animation.thumbs[0].file_size, None, ())))
        # send_video потому что нужно стараться превращать гифки в видосы
        return await cl.send_video(msg.chat.id, path, caption=caption, duration=mess.animation.duration, width=mess.animation.width, height=mess.animation.height, thumb=thumb, progress=__upload_progress, progress_args=(msg,))
    elif mess.media == MessageMediaType.VIDEO_NOTE:
        thumb = str(await cl.handle_download((FileId.decode(mess.video_note.thumbs[0].file_id), "./downloads/", mess.video_note.thumbs[0].file_id + ".jpg", False, mess.video_note.thumbs[0].file_size, None, ())))
        return await cl.send_video_note(msg.chat.id, path, duration=mess.video_note.duration, thumb=thumb, progress=__upload_progress, progress_args=(msg,))
    elif mess.media == MessageMediaType.AUDIO:
        return await cl.send_audio(msg.chat.id, path, caption=caption, progress=__upload_progress, progress_args=(msg,))
    elif mess.media == MessageMediaType.VOICE:
        return await cl.send_voice(msg.chat.id, path, caption=caption, progress=__upload_progress, progress_args=(msg,))
    else:
        return await cl.send_document(msg.chat.id, path, caption=caption, progress=__upload_progress, progress_args=(msg,))


async def check_subscribe_steal_func(_, __, msg: Message):
    base = sqlite3.connect("main_base.db")
    cur = base.cursor()
    subscribe_ids = cur.execute("SELECT * FROM subscribes").fetchall()
    for subscribe_id in subscribe_ids:
        if msg.chat.id == subscribe_id[0]: # [0] потому что fetchall возвращает список кортежей
            base.close()
            return True
    base.close()
    return False
subscribesteal_filter = filters.create(check_subscribe_steal_func)


async def subscribesteal_filter_func(cl: Client, msg: Message):
    mess = Message(id=0)
    mess.chat = Chat(id=config.STEAL_SAVER_CHANNEL, type=ChatType.CHANNEL)
    res: Message = await __send_media(cl, mess, msg)
    if res:
        await cl.send_message(config.STEAL_SAVER_CHANNEL, f"https://t.me/c/{-(msg.chat.id + 1_000_000_000_000)}/{msg.id}", reply_to_message_id=res.id)
        await cl.mark_chat_unread(config.STEAL_SAVER_CHANNEL)

        if Path("downloads").exists():
            for p in Path("downloads").iterdir():
                try:
                    os.remove(p)
                except FileNotFoundError:
                    pass
        
        try:
            os.removedirs("downloads")
        except FileNotFoundError:
            pass


for a in apps:
    a.add_handler(MessageHandler(subscribesteal_filter_func, subscribesteal_filter))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS subscribes (id INT PRIMARY KEY)")
base.commit()
base.close()
