from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".getallcodefiles": "<code>.getallcodefiles</code>  —  получение всех файлов с кодом и тд\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
}


# Получение всех файлов с кодом и тд
async def getallcodefiles_command_func(cl: Client, msg: Message):
    await msg.delete()

    await cl.send_document(msg.chat.id, "main.py")
    await cl.send_document(msg.chat.id, "patch_dispatcher.py")
    await cl.send_document(msg.chat.id, "config.py")
    await cl.send_document(msg.chat.id, "config.ini")
    await cl.send_document(msg.chat.id, "requirements.txt")
    await cl.send_document(msg.chat.id, "main_base.db")
    await cl.send_document(msg.chat.id, "free_usernames.txt")
    await cl.send_document(msg.chat.id, "free_usernames2.txt")


for a in apps:
    a.add_handler(MessageHandler(getallcodefiles_command_func, filters.command("getallcodefiles", prefixes=".") & filters.user("me")))
