import os
import config
from utils import send_temp_message
from pathlib import Path
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.file_id import FileId
from pyrogram.handlers import MessageHandler
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.types.user_and_chats.dialog import Dialog
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".steal": "<code>.steal</code>  —  копируем медиафайлы с каналов с запретом на сохранение контента\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - (пишется на новой строке, а не через пробел) айди целевого канала или его название; нужно учитывать,"+
                                " что при копировании ссылки с телеграма айди имеет одинаковый формат для любого чата, а в програме нет, соответственно к айди"+
                                " группового чата нужно добавить число 1 000 000 000 000, а к айди супергруппы или канала добавить то же число и дописать минус в начале;"+
                                " личные чаты не меняются; не рекомендуется применять команду к чему-то кроме каналов\n"+
                        "    __**Второй параметр:**__ (необязательно) - (пишется на новой строке, а не через пробел) айди целевого поста; если не указано,"+
                                " то будет итеративно скопирован весь канал по одному медиафайлу за раз"
    },
    "en": {
        ".steal": "<code>.steal</code>  —  copy media files from channels with a restriction to saving content\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - (is written on a new line, not separated by a space) id of target channel or him name; need to consider,"+
                                " that when copying a link from Telegram id has the same format for any chat, but in the program does not, so you need to add a number"+
                                " 1 000 000 000 000 to the group chat id, and add the same number to the supergroup or channel id and add a minus in the beginning;"+
                                " private chats don't change; it is not recommended to apply the command to anything other than channels\n"+
                        "    __**Second param:**__ (not required) - (is written on a new line, not separated by a space) id of target post; if not set,"+
                                " then the whole channel will be iteratively copied by one media file at a time"
    }
}


PHRASES_VAR = {
    "ru": {
        "downloading": "Загрузка: {0} %",
        "uploading": "Отправка: {0} %",
        "require_param": "Требуется параметр - название чата или его айди",
        "total_posts": "Общее количество постов: {0}",
        "processed_posts": "Обработано постов: {0} из {1}",
        "dialog_not_found": "Диалог с таким названием или айди не найден"
    },
    "en": {
        "downloading": "Downloading: {0} %",
        "uploading": "Uploading: {0} %",
        "require_param": "Require param - name of chat or him id",
        "total_posts": "Total posts: {0}",
        "processed_posts": "Processed posts: {0} from {1}",
        "dialog_not_found": "Dialog with this name or id not found"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def __download_progress(current: int, total: int, msg: Message):
    if msg.text:
        await msg.edit_text(get_phrase("downloading").format(int(current/total*100)))


async def __upload_progress(current: int, total: int, msg: Message):
    if msg.text:
        await msg.edit_text(get_phrase("uploading").format(int(current/total*100)))


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


async def steal_command_func(cl: Client, msg: Message):
    await msg.edit_text(".")

    try:
        chat_name_or_id = msg.text.split("\n")[1]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_param"))
        return

    try:
        id = int(msg.text.split("\n")[2])
    except IndexError:
        id = None

    async for dialog in cl.get_dialogs():
        dialog: Dialog
        if dialog.chat.title == chat_name_or_id or (dialog.chat.id == int(chat_name_or_id) if (chat_name_or_id[1:] if chat_name_or_id.startswith("-") else chat_name_or_id).isdigit() else False):
            if id:
                await __send_media(cl, msg, await cl.get_messages(dialog.chat.id, id))
            else:
                all = await cl.get_chat_history_count(int(chat_name_or_id) if (chat_name_or_id[1:] if chat_name_or_id.startswith("-") else chat_name_or_id).isdigit() else chat_name_or_id)
                mess = await cl.send_message(msg.chat.id, get_phrase("total_posts").format(all))
                count = 0
                async for m in cl.get_chat_history(dialog.chat.id):
                    await __send_media(cl, msg, m)
                    count += 1
                    await mess.edit_text(get_phrase("processed_posts").format(count, all))
                await mess.delete()
            break
    else:
        await send_temp_message(cl, msg.chat.id, get_phrase("dialog_not_found"))
    
    await msg.delete()

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
    a.add_handler(MessageHandler(steal_command_func, filters.command("steal", prefixes=".") & filters.user("me")))
