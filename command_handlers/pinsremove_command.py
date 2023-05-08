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
        ".pinsremove": "<code>.pinsremove</code>  —  управление \"мониторингом\" каналов на предмет новых сообщений о закрепе (такие будут сразу удаляться)\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевое действие; варианты: \"add\" - добавить айди канала в список мониторинга закрепов,"+
                                " \"delete\" - удалить айди канала из списка мониторинга закрепов, \"items\"  - получить все элементы из списка мониторинга закрепов,"+
                                " \"clearall\" - полностью очистить список мониторинга закрепов\n"+
                        "    __**Второй параметр:**__ (необязательно) - айди целевого канала; нужно учитывать, что при копировании ссылки с телеграма"+
                                " айди имеет одинаковый формат для любого чата, а в программе нет, соответственно к айди группового чата нужно добавить"+
                                " число 1 000 000 000 000, а к айди супергруппы или канала добавить то же число и дописать минус в начале; личные чаты не меняются"
    },
    "en": {
        ".pinsremove": "<code>.pinsremove</code>  —  manage \"monitoring\" channel for new pinned messages (those will be deleted automatically)\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) -  tagret operation; variants: \"add\" - add id of channel to pins monitoring list,"+
                                " \"delete\" - delete id of channel from pins monitoring list, \"items\"  - get all items from из pins monitoring list,"+
                                " \"clearall\" - clear pins monitoring list\n"+
                        "    __**Second param:**__ (not required) - id of target channel; need to consider, that when copying a link from Telegram"+
                                " id has the same format for any chat, but in the program does not, so you need to add a number 1 000 000 000 000"+
                                " to the group chat id, and add the same number to the supergroup or channel id and add a minus in the beginning; private chats don't change"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_param": "Требуется параметр действия",
        "require_num_param": "Требуется числовой параметр (айди)",
        "id_already_added": "Айди уже в списке мониторинга закрепов",
        "id_succesful_added": "Айди успешно добавлено в список мониторинга закрепов",
        "id_successful_deleted": "Айди успешно удалено из списка мониторинга закрепов",
        "id_not_in_list": "Айди нет в списке мониторинга закрепов",
        "total_items": "Всего элементов: {0}",
        "all_items_deleted": "Все айди успешно удалены из списка мониторинга закрепов",
        "incorrect_param": "Неверный параметр"
    },
    "en": {
        "require_param": "Require param of action",
        "require_num_param": "Require numeric param (id)",
        "id_already_added": "Id already in pins monitoring list",
        "id_succesful_added": "Id successful added to pins monitoring list",
        "id_successful_deleted": "Id successful deleted from pins monitoring list",
        "id_not_in_list": "Id not in pins monitoring list",
        "total_items": "Total items: {0}",
        "all_items_deleted": "All ids successful deleted from pins monitoring list",
        "incorrect_param": "Incorrect param"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def pinsremove_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        action = msg.text.split(" ", maxsplit=2)[1]
    except IndexError:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_param"))
        return
    
    try:
        id = int(msg.text.split(" ", maxsplit=2)[2])
    except (IndexError, TypeError):
        id = None
    
    base = sqlite3.connect("main_base.db")
    cur = base.cursor()

    if action == "add":
        if not id:
            await send_temp_message(cl, msg.chat.id, get_phrase("require_num_param"))
            return

        try:
            cur.execute("INSERT INTO pins VALUES (?)", (id,))
        except sqlite3.IntegrityError:
            await send_temp_message(cl, msg.chat.id, get_phrase("id_already_added"))
        else:
            log("----------PINS ID SUCCESFULLY ADDED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, get_phrase("id_succesful_added"))
    elif action == "delete":
        if not id:
            await send_temp_message(cl, msg.chat.id, get_phrase("require_num_param"))
            return

        if cur.execute("SELECT id FROM pins WHERE id=?", (id,)).fetchone():
            cur.execute("DELETE FROM pins WHERE id=?", (id,))
            log("----------PINS ID SUCCESFULLY REMOVED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, get_phrase("id_successful_deleted"))
        else:
            await send_temp_message(cl, msg.chat.id, get_phrase("id_not_in_list"))
    elif action == "items":
        pins_ids = cur.execute("SELECT * FROM pins").fetchall()
        log("----------GET PINS IDS LIST----------", LogMode.INFO)
        for pin_id in pins_ids:
            await cl.send_message(msg.chat.id, pin_id[0]) # [0] потому что fetchall возвращает список кортежей
        await cl.send_message(msg.chat.id, get_phrase("total_items").format(len(pin_id)))
    elif action == "clearall":
        cur.execute("DELETE FROM pins")
        log("----------ALL PINS IDS REMOVED----------", LogMode.INFO)
        await send_temp_message(cl, msg.chat.id, get_phrase("all_items_deleted"))
    else:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorrect_param"))
    
    base.commit()
    base.close()


for a in apps:
    a.add_handler(MessageHandler(pinsremove_command_func, filters.command("pinsremove", prefixes=".") & filters.user("me")))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS pins (id INT PRIMARY KEY)")
base.commit()
base.close()
