from on_start import apps

from pyrogram import filters
from pyrogram.raw import functions
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".screenshot": "<code>.screenshot</code>  —  создание сервисного сообщения о сделанном скриншоте\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Создание сервисного сообщения о сделанном скриншоте
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
