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
        ".get": "<code>.get</code>  —  получение поста из канала по его айди\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди канала\n"+
                        "    __**Второй параметр:**__ (обязательно) - айди поста"
    },
    "en": {
        ".get": "<code>.get</code>  —  get post from channel by him id\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - id of channel\n"+
                        "    __**Second param:**__ (required) - id of post"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_id_of_channel": "Требуется айди целевого канала",
        "require_id_of_post": "Требуется айди целевого поста",
        "post_too_long": "Пост слишком большой"
    },
    "en": {
        "require_id_of_channel": "Require id of target channel",
        "require_id_of_post": "Require id of target post",
        "post_too_long": "Post too long"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def get_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        chat_id = int(msg.text.split(" ", maxsplit=2)[1])
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_id_of_channel"))
        return
        
    try:
        post_id = int(msg.text.split(" ", maxsplit=2)[2])
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_id_of_post"))
        return
    
    post = await cl.get_messages(chat_id, post_id)
    log(str(post), LogMode.INFO)
    try:
        await cl.send_message(msg.chat.id, post)
    except exceptions.bad_request_400.MessageTooLong:
        log("----------POST TOO LONG----------", LogMode.ERROR)
        await send_temp_message(cl, msg.chat.id, get_phrase("post_too_long"))
        with open(f"post_{post.id}.txt", "w", encoding="utf-8") as f:
            f.write(str(post))
        await cl.send_document(msg.chat.id, f"post_{post.id}.txt")


for a in apps:
    a.add_handler(MessageHandler(get_command_func, filters.command("get", prefixes=".") & filters.user("me")))
