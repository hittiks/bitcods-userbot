import importlib
from utils import send_temp_message
from pathlib import Path
from on_start import apps

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".help": "<code>.help</code>  —  команда для справки\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (необязательно) - команда (отобразится её подробное описание)"
}


# Команда для справки
async def help_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        key = msg.text.split(".help ", maxsplit=1)[1]
    except IndexError:
        key = ""
    
    list_of_key = {

    }

    temp_dict = dict()
    keys_string = ""
    for p in Path("command_handlers").absolute().iterdir():
        if not p.stem.startswith("__"):
            module = importlib.import_module("." + p.stem, __package__)
            k,v = [(x, y) for x, y in module.__dict__["HELP_VAR"].items()][0]
            temp_dict[k] = v
            keys_string += f"<code>{k}</code>\n"
    
    list_of_key[""] = (
            "**Доступные команды:**\n"+
                        keys_string +
                        "\n"+
                "**Для получения подробной информации о команде введи <code>.help</code> <команда>**\n\nКоманда <code>.help all</code> выведет всю справку\n\n"+
                "**Примечание:   __Если команда имеет обязательный параметр, то без него она не сработает__**")
    
    for k, v in temp_dict.items():
        list_of_key[k] = v

    if key == "all":
        text = ""
        counter = 0
        for x in list_of_key:
            cp = text + list_of_key[x] + "\n\n▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇\n\n"
            if len(cp) >= 4000:
                await cl.send_message(msg.chat.id, text)
                text = list_of_key[x] + "\n\n▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇\n\n"
                counter = 1
            else:
                text = cp
                counter += 1
        if counter > 0:
            await cl.send_message(msg.chat.id, text[:-24])
    else:
        try:
            await cl.send_message(msg.chat.id, list_of_key[key])
        except KeyError:
            await send_temp_message(cl, msg.chat.id, "Неизвестная команда")


for a in apps:
    a.add_handler(MessageHandler(help_command_func, filters.command("help", prefixes=".") & filters.user("me")))
