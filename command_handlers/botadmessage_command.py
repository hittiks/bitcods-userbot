import sqlite3
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".botadmessage": "<code>.botadmessage</code>  —  управление \"чёрным списком\" рекламы от ботов (такая автоматически удаляется)\n"+
                "__**В зависимости от целевого действия обязательно отправлять ответом на целевое сообщение или нет**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевое действие; варианты: \"ban\" - добавить текст из целевого сообщения в чёрный список,"+
                                " \"unban\" - удалить текст из целевого сообщения с чёрного списка, \"items\"  - получить все элементы из чёрного списка,"+
                                " \"clearall\" - полностью очистить чёрный список"
}


# Управление "чёрным списком" рекламы от ботов (такая автоматически удаляется)
async def botadmessage_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        action = msg.text.split(".botadmessage ", maxsplit=1)[1]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Требуется параметр действия")
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
                await send_temp_message(cl, msg.chat.id, "Команда должна быть ответом на сообщение")
                return

            try:
                cur.execute("INSERT INTO ads VALUES (?)", (text,))
            except sqlite3.IntegrityError:
                await send_temp_message(cl, msg.chat.id, "Реклама уже в чёрном списке")
            else:
                log("----------BOT AD MESSAGE BANNED----------", LogMode.INFO)
                await send_temp_message(cl, msg.chat.id, "Реклама успешно добавлена в чёрный список")
        except AttributeError:
            await send_temp_message(cl, msg.chat.id, "Команда с этим флагом должна быть ответом на сообщение")
    elif action == "unban":
        try:
            if msg.reply_to_message.text:
                text = msg.reply_to_message.text
            elif msg.reply_to_message.caption:
                text = msg.reply_to_message.caption
            else:
                await send_temp_message(cl, msg.chat.id, "Команда должна быть ответом на сообщение")
                return

            if cur.execute("SELECT ad FROM ads WHERE ad=?", (text,)).fetchone():
                cur.execute("DELETE FROM ads WHERE ad=?", (text,))
                log("----------BOT AD MESSAGE UNBANNED----------", LogMode.INFO)
                await send_temp_message(cl, msg.chat.id, "Реклама успешно удалена из чёрного списка")
            else:
                await send_temp_message(cl, msg.chat.id, "Рекламы нет в чёрном списке")
        except AttributeError:
            await send_temp_message(cl, msg.chat.id, "Команда с этим флагом должна быть ответом на сообщение")
    elif action == "items":
        ads = cur.execute("SELECT * FROM ads").fetchall()
        log("----------GET BOT ADS LIST----------", LogMode.INFO)
        for ad in ads:
            await cl.send_message(msg.chat.id, ad[0]) # [0] потому что fetchall возвращает список кортежей
        await cl.send_message(msg.chat.id, f"Всего элементов: {len(ads)}")
    elif action == "clearall":
        cur.execute("DELETE FROM ads")
        log("----------ALL BOT AD MESSAGES UNBANNED----------", LogMode.INFO)
        await send_temp_message(cl, msg.chat.id, "Вся реклама успешно удалена из чёрного списка")
    else:
        await send_temp_message(cl, msg.chat.id, "Неверный параметр")
    
    base.commit()
    base.close()


for a in apps:
    a.add_handler(MessageHandler(botadmessage_command_func, filters.command("botadmessage", prefixes=".") & filters.user("me")))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS ads (ad TEXT PRIMARY KEY)")
base.commit()
base.close()
