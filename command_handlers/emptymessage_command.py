from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".emptymessage": "<code>.emptymessage</code>  —  отправка \"пустого\" сообщения (отправляется один неотображаемый символ)\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Отправка "пустого" сообщения (отправляется один неотображаемый символ)
async def emptymessage_command_func(cl: Client, msg: Message):
    await msg.delete()
            
    hidden_symbol = "⁠" #it's not empty, just not displayed
    await cl.send_message(msg.chat.id, hidden_symbol)


for a in apps:
    a.add_handler(MessageHandler(emptymessage_command_func, filters.command("emptymessage", prefixes=".") & filters.user("me")))
