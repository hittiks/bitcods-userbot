import sqlite3
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".pinsremove": "<code>.pinsremove</code>  —  управление \"мониторингом\" каналов на предмет новых сообщений о закрепе (такие будут сразу удаляться)\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевое действие; варианты: \"add\" - добавить айди канала в список мониторинга закрепов,"+
                                " \"delete\" - удалить айди канала из списка мониторинга закрепов, \"items\"  - получить все элементы из списка мониторинга закрепов,"+
                                " \"clearall\" - полностью очистить список мониторинга закрепов\n"+
                        "    __**Второй параметр:**__ (необязательно) - айди целевого канала; нужно учитывать, что при копировании ссылки с телеграма"+
                                " айди имеет одинаковый формат для любого чата, а в пирограме нет, соответственно к айди группового чата нужно добавить"+
                                " число 1 000 000 000 000, а к айди супергруппы или канала добавить то же число и дописать минус в начале; личные чаты не меняются"
}


# Управление "мониторингом" каналов на предмет новых сообщений о закрепе (такие будут сразу удаляться)
async def pinsremove_command_func(cl: Client, msg: Message):
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

    if action == "add":
        if not id:
            await send_temp_message(cl, msg.chat.id, "Требуется числовой параметр (айди)")
            return

        try:
            cur.execute("INSERT INTO pins VALUES (?)", (id,))
        except sqlite3.IntegrityError:
            await send_temp_message(cl, msg.chat.id, "Айди уже в списке мониторинга закрепов")
        else:
            log("----------PINS ID SUCCESFULLY ADDED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, "Айди успешно добавлено в список мониторинга закрепов")
    elif action == "delete":
        if not id:
            await send_temp_message(cl, msg.chat.id, "Требуется числовой параметр (айди)")
            return

        if cur.execute("SELECT id FROM pins WHERE id=?", (id,)).fetchone():
            cur.execute("DELETE FROM pins WHERE id=?", (id,))
            log("----------PINS ID SUCCESFULLY REMOVED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, "Айди успешно удалено из списка мониторинга закрепов")
        else:
            await send_temp_message(cl, msg.chat.id, "Айди нет в списке мониторинга закрепов")
    elif action == "items":
        pins_ids = cur.execute("SELECT * FROM pins").fetchall()
        log("----------GET PINS IDS LIST----------", LogMode.INFO)
        for pin_id in pins_ids:
            await cl.send_message(msg.chat.id, pin_id[0]) # [0] потому что fetchall возвращает список кортежей
        await cl.send_message(msg.chat.id, f"Всего элементов: {len(pin_id)}")
    elif action == "clearall":
        cur.execute("DELETE FROM pins")
        log("----------ALL PINS IDS REMOVED----------", LogMode.INFO)
        await send_temp_message(cl, msg.chat.id, "Все айди успешно удалены из списка мониторинга закрепов")
    else:
        await send_temp_message(cl, msg.chat.id, "Неверный параметр действия")
    
    base.commit()
    base.close()


for a in apps:
    a.add_handler(MessageHandler(pinsremove_command_func, filters.command("pinsremove", prefixes=".") & filters.user("me")))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS pins (id INT PRIMARY KEY)")
base.commit()
base.close()
