import config
import sqlite3
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".botadmessage": "<code>.botadmessage</code>  —  управление \"чёрным списком\" рекламы от ботов (такая автоматически удаляется)\n"+
                "__**В зависимости от целевого действия обязательно отправлять ответом на целевое сообщение или нет**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевое действие; варианты: \"ban\" - добавить текст из целевого сообщения в чёрный список,"+
                                " \"unban\" - удалить текст из целевого сообщения с чёрного списка, \"items\"  - получить все элементы из чёрного списка,"+
                                " \"clearall\" - полностью очистить чёрный список"
    },
    "en": {
        ".botadmessage": "<code>.botadmessage</code>  —  manage \"black list\" of ads from bot (those will be deleted automatically)\n"+
                "__**Depending on the target action is necessary to send a command to the target message or not**__\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - tagret operation; variants: \"ban\" - add text of target message to black list,"+
                                " \"unban\" - delete text of target message from black list, \"items\"  - show all items from black list,"+
                                " \"clearall\" - clear all items from black list"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_param": "Требуется параметр действия",
        "need_reply": "Команда должна быть ответом на сообщение",
        "ad_already_banned": "Реклама уже в чёрном списке",
        "ad_succesful_banned": "Реклама успешно добавлена в чёрный список",
        "need_flag_reply": "Команда с этим флагом должна быть ответом на сообщение",
        "ad_successful_deleted": "Реклама успешно удалена из чёрного списка",
        "ad_not_in_list": "Рекламы нет в чёрном списке",
        "total_items": "Всего элементов: {0}",
        "all_items_deleted": "Вся реклама успешно удалена из чёрного списка",
        "incorrect_param": "Неверный параметр"
    },
    "en": {
        "require_param": "Require param of action",
        "need_reply": "The command must be a reply to a message",
        "ad_already_banned": "Ad already in black list",
        "ad_succesful_banned": "Ad successful added to black list",
        "need_flag_reply": "The command with this flag must be a reply to a message",
        "ad_successful_deleted": "Ad successful deleted from black list",
        "ad_not_in_list": "Ad not in black list",
        "total_items": "Total items: {0}",
        "all_items_deleted": "All ads successful deleted from black list",
        "incorrect_param": "Incorrect param"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def botadmessage_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        action = msg.text.split(".botadmessage ", maxsplit=1)[1]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_param"))
        return
    
    base = sqlite3.connect("main_base.db")
    cur = base.cursor()

    if action == "ban":
        try:
            if msg.reply_to_message.text:
                text = msg.reply_to_message.text
            elif msg.reply_to_message.caption:
                text = msg.reply_to_message.caption
            else:
                await send_temp_message(cl, msg.chat.id, get_phrase("need_reply"))
                return

            try:
                cur.execute("INSERT INTO ads VALUES (?)", (text,))
            except sqlite3.IntegrityError:
                await send_temp_message(cl, msg.chat.id, get_phrase("ad_already_banned"))
            else:
                log("----------BOT AD MESSAGE BANNED----------", LogMode.INFO)
                await send_temp_message(cl, msg.chat.id, get_phrase("ad_succesful_banned"))
        except AttributeError:
            await send_temp_message(cl, msg.chat.id, get_phrase("need_flag_reply"))
    elif action == "unban":
        try:
            if msg.reply_to_message.text:
                text = msg.reply_to_message.text
            elif msg.reply_to_message.caption:
                text = msg.reply_to_message.caption
            else:
                await send_temp_message(cl, msg.chat.id, get_phrase("need_reply"))
                return

            if cur.execute("SELECT ad FROM ads WHERE ad=?", (text,)).fetchone():
                cur.execute("DELETE FROM ads WHERE ad=?", (text,))
                log("----------BOT AD MESSAGE UNBANNED----------", LogMode.INFO)
                await send_temp_message(cl, msg.chat.id, get_phrase("ad_successful_deleted"))
            else:
                await send_temp_message(cl, msg.chat.id, get_phrase("ad_not_in_list"))
        except AttributeError:
            await send_temp_message(cl, msg.chat.id, get_phrase("need_flag_reply"))
    elif action == "items":
        ads = cur.execute("SELECT * FROM ads").fetchall()
        log("----------GET BOT ADS LIST----------", LogMode.INFO)
        for ad in ads:
            await cl.send_message(msg.chat.id, ad[0]) # [0] потому что fetchall возвращает список кортежей
        await cl.send_message(msg.chat.id, get_phrase("total_items").format(len(ads)))
    elif action == "clearall":
        cur.execute("DELETE FROM ads")
        log("----------ALL BOT AD MESSAGES UNBANNED----------", LogMode.INFO)
        await send_temp_message(cl, msg.chat.id, get_phrase("all_items_deleted"))
    else:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorrect_param"))
    
    base.commit()
    base.close()


for a in apps:
    a.add_handler(MessageHandler(botadmessage_command_func, filters.command("botadmessage", prefixes=".") & filters.user("me")))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS ads (ad TEXT PRIMARY KEY)")
base.commit()
base.close()
