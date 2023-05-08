import config
from pathlib import Path
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".getfiles": "<code>.getfiles</code>  —  получение всех файлов с кодом и тд (используй только в чате \"Избранное\","+
        " так как файлы с аккаунтом и личными данными тоже будут отправлены)\n"+
                "==============================\n<u>Параметры</u>:\n    ~~Не имеет~~"
    },
    "en": {
        ".getfiles": "<code>.getfiles</code>  —  getting all files with code etc (use only in chat \"Saved messages\","+
        " because files with accound and private data also will be send)\n"+
                "==============================\n<u>Params</u>:\n    ~~Doesn't have~~"
    }
}


PHRASES_VAR = {
    "ru": {
        "from_folder": "Из папки {0}"
    },
    "en": {
        "from_folder": "From folder {0}"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def getallcodefiles_command_func(cl: Client, msg: Message):
    await msg.delete()

    for path in Path(".").absolute().iterdir():
        if path.name.startswith(".") or path.name == "__pycache__":
            continue
        
        if path.is_file():
            await cl.send_document(msg.chat.id, path)
        else:
            for sub_path in path.iterdir():
                if sub_path.name.startswith(".") or sub_path.name == "__pycache__":
                    continue

                await cl.send_document(msg.chat.id, sub_path, caption=get_phrase("from_folder").format(path.name))


for a in apps:
    a.add_handler(MessageHandler(getallcodefiles_command_func, filters.command("getallcodefiles", prefixes=".") & filters.user("me")))
