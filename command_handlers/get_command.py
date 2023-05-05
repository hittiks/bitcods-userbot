from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".get": "<code>.get</code>  —  получение поста из канала по его айди\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди канала\n"+
                        "    __**Второй параметр:**__ (обязательно) - айди поста"
}


# Получение поста из канала по его айди
async def get_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        chat_id = int(msg.text.split(" ", maxsplit=2)[1])
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Требуется айди целевого канала")
        return
        
    try:
        post_id = int(msg.text.split(" ", maxsplit=2)[2])
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Требуется айди целевого поста")
        return
    
    post = await cl.get_messages(chat_id, post_id)
    log(str(post), LogMode.INFO)
    try:
        await cl.send_message(msg.chat.id, post)
    except exceptions.bad_request_400.MessageTooLong:
        log("----------POST TOO LONG----------", LogMode.ERROR)
        await send_temp_message(cl, msg.chat.id, "Пост слишком большой")
        with open(f"post_{post.id}.txt", "w", encoding="utf-8") as f:
            f.write(str(post))
        await cl.send_document(msg.chat.id, f"post_{post.id}.txt")


for a in apps:
    a.add_handler(MessageHandler(get_command_func, filters.command("get", prefixes=".") & filters.user("me")))
