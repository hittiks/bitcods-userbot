import sqlite3
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".subscribesteal": "<code>.subscribesteal</code>  —  управление \"подпиской\" на каналы с запретом на пересылку (контент из таких автоматически стилится в определённый канал)\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевое действие; варианты: \"subscribe\" - добавить айди канала в список подписок,"+
                                " \"unsubscribe\" - удалить айди канала из списка подписок, \"items\"  - получить все элементы из списка подписок,"+
                                " \"clearall\" - полностью очистить список подписок\n"+
                        "    __**Второй параметр:**__ (необязательно) - айди целевого канала; нужно учитывать, что при копировании ссылки с телеграма"+
                                " айди имеет одинаковый формат для любого чата, а в пирограме нет, соответственно к айди группового чата нужно добавить"+
                                " число 1 000 000 000 000, а к айди супергруппы или канала добавить то же число и дописать минус в начале; личные чаты не меняются"
}


# Управление "подпиской" на каналы с запретом на пересылку (контент из таких автоматически стилится в определённый канал)
async def subscribesteal_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        action = msg.text.split(" ", maxsplit=2)[1]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, "Требуется параметр действия")
        return
    
    try:
        id = int(msg.text.split(" ", maxsplit=2)[2])
    except (IndexError, TypeError):
        id = None
    
    base = sqlite3.connect("main_base.db")
    cur = base.cursor()

    if action == "subscribe":
        if not id:
            await send_temp_message(cl, msg.chat.id, "Требуется числовой параметр (айди)")
            return

        try:
            cur.execute("INSERT INTO subscribes VALUES (?)", (id,))
        except sqlite3.IntegrityError:
            await send_temp_message(cl, msg.chat.id, "Айди уже в списке подписок")
        else:
            log("----------SUBSCRIBE ID SUCCESFULLY ADDED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, "Айди успешно добавлено в список подписок")
    elif action == "unsubscribe":
        if not id:
            await send_temp_message(cl, msg.chat.id, "Требуется числовой параметр (айди)")
            return

        if cur.execute("SELECT id FROM subscribes WHERE id=?", (id,)).fetchone():
            cur.execute("DELETE FROM subscribes WHERE id=?", (id,))
            log("----------SUBSCRIBE ID SUCCESFULLY REMOVED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, "Айди успешно удалено из списка подписок")
        else:
            await send_temp_message(cl, msg.chat.id, "Айди нет в списке подписок")
    elif action == "items":
        subscribe_ids = cur.execute("SELECT * FROM subscribes").fetchall()
        log("----------GET SUBSCRIBE IDS LIST----------", LogMode.INFO)
        for subscribe_id in subscribe_ids:
            await cl.send_message(msg.chat.id, subscribe_id[0]) # [0] потому что fetchall возвращает список кортежей
        await cl.send_message(msg.chat.id, f"Всего элементов: {len(subscribe_ids)}")
    elif action == "clearall":
        cur.execute("DELETE FROM subscribes")
        log("----------ALL SUBSCRIBE IDS REMOVED----------", LogMode.INFO)
        await send_temp_message(cl, msg.chat.id, "Все айди успешно удалены из списка подписок")
    else:
        await send_temp_message(cl, msg.chat.id, "Неверный параметр действия")
    
    base.commit()
    base.close()


for a in apps:
    a.add_handler(MessageHandler(subscribesteal_command_func, filters.command("subscribesteal", prefixes=".") & filters.user("me")))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS subscribes (id INT PRIMARY KEY)")
base.commit()
base.close()
