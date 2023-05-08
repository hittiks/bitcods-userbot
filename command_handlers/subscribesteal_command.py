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
        ".subscribesteal": "<code>.subscribesteal</code>  —  управление \"подпиской\" на каналы с запретом на копирование контента"+
                        " (контент из таких автоматически копируется в определённый канал)\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - целевое действие; варианты: \"subscribe\" - добавить айди канала в список подписок,"+
                                " \"unsubscribe\" - удалить айди канала из списка подписок, \"items\"  - получить все элементы из списка подписок,"+
                                " \"clearall\" - полностью очистить список подписок\n"+
                        "    __**Второй параметр:**__ (необязательно) - айди целевого канала; нужно учитывать, что при копировании ссылки с телеграма"+
                                " айди имеет одинаковый формат для любого чата, а в пирограме нет, соответственно к айди группового чата нужно добавить"+
                                " число 1 000 000 000 000, а к айди супергруппы или канала добавить то же число и дописать минус в начале; личные чаты не меняются"
    },
    "en": {
        ".subscribesteal": "<code>.subscribesteal</code>  —  management of \"subscription\" to channels with a restriction to copying content"+
                        " (content from such channels is automatically copied to a specific channel)\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - targeted action; variants: \"subscribe\" - add id of channel to list of subscribes,"+
                                " \"unsubscribe\" - delete id of cannel from list of subscribes, \"items\"  - get all items from list of subscribes,"+
                                " \"clearall\" - clear list of subscribes\n"+
                        "    __**Second param:**__ (not required) - id of target channel; need to consider, that when copying a link from Telegram"+
                                " id has the same format for any chat, but in the program does not, so you need to add a number 1 000 000 000 000"+
                                " to the group chat id, and add the same number to the supergroup or channel id and add a minus in the beginning; private chats don't change"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_param": "Требуется параметр действия",
        "require_num_param": "Требуется числовой параметр (айди)",
        "id_already_added": "Айди уже в списке подписок",
        "id_succesful_added": "Айди успешно добавлено в список подписок",
        "id_successful_deleted": "Айди успешно удалено из списка подписок",
        "id_not_in_list": "Айди нет в списке подписок",
        "total_items": "Всего элементов: {0}",
        "all_items_deleted": "Все айди успешно удалены из списка подписок",
        "incorrect_param": "Неверный параметр"
    },
    "en": {
        "require_param": "Require param of action",
        "require_num_param": "Require numeric param (id)",
        "id_already_added": "Id already in subscribes list",
        "id_succesful_added": "Id successful added to subscribes list",
        "id_successful_deleted": "Id successful deleted from subscribes list",
        "id_not_in_list": "Id not in subscribes list",
        "total_items": "Total items: {0}",
        "all_items_deleted": "All ids successful deleted from subscribes list",
        "incorrect_param": "Incorrect param"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def subscribesteal_command_func(cl: Client, msg: Message):
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

    if action == "subscribe":
        if not id:
            await send_temp_message(cl, msg.chat.id, get_phrase("require_num_param"))
            return

        try:
            cur.execute("INSERT INTO subscribes VALUES (?)", (id,))
        except sqlite3.IntegrityError:
            await send_temp_message(cl, msg.chat.id, get_phrase("id_already_added"))
        else:
            log("----------SUBSCRIBE ID SUCCESFULLY ADDED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, get_phrase("id_succesful_added"))
    elif action == "unsubscribe":
        if not id:
            await send_temp_message(cl, msg.chat.id, get_phrase("require_num_param"))
            return

        if cur.execute("SELECT id FROM subscribes WHERE id=?", (id,)).fetchone():
            cur.execute("DELETE FROM subscribes WHERE id=?", (id,))
            log("----------SUBSCRIBE ID SUCCESFULLY REMOVED----------", LogMode.INFO)
            await send_temp_message(cl, msg.chat.id, get_phrase("id_successful_deleted"))
        else:
            await send_temp_message(cl, msg.chat.id, get_phrase("id_not_in_list"))
    elif action == "items":
        subscribe_ids = cur.execute("SELECT * FROM subscribes").fetchall()
        log("----------GET SUBSCRIBE IDS LIST----------", LogMode.INFO)
        for subscribe_id in subscribe_ids:
            await cl.send_message(msg.chat.id, subscribe_id[0]) # [0] потому что fetchall возвращает список кортежей
        await cl.send_message(msg.chat.id, get_phrase("total_items").format(len(subscribe_ids)))
    elif action == "clearall":
        cur.execute("DELETE FROM subscribes")
        log("----------ALL SUBSCRIBE IDS REMOVED----------", LogMode.INFO)
        await send_temp_message(cl, msg.chat.id, get_phrase("all_items_deleted"))
    else:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorrect_param"))
    
    base.commit()
    base.close()


for a in apps:
    a.add_handler(MessageHandler(subscribesteal_command_func, filters.command("subscribesteal", prefixes=".") & filters.user("me")))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS subscribes (id INT PRIMARY KEY)")
base.commit()
base.close()
