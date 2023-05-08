import config
from on_start import apps

from pyrogram import filters
from pyrogram.raw import functions
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".screenshot": "<code>.screenshot</code>  —  создание сервисного сообщения о сделанном скриншоте\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
    },
    "en": {
        ".screenshot": "<code>.screenshot</code>  —  creating a service message about the screenshot taken\n"+
                "==============================\n<u>Params</u>:\n    ~~Doesn't have~~"
    }
}


PHRASES_VAR = {
    "ru": {
        "<empty>": "<empty>"
    },
    "en": {
        "<empty>": "<empty>"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def screenshot_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    send = functions.messages.SendScreenshotNotification(
        peer = await cl.resolve_peer(msg.chat.id),
        reply_to_msg_id = 0,
        random_id = cl.rnd_id(),
    )

    await cl.invoke(send)


for a in apps:
    a.add_handler(MessageHandler(screenshot_command_func, filters.command("screenshot", prefixes=".") & filters.user("me")))
