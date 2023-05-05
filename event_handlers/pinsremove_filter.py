import config
import sqlite3
from on_start import apps

from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.enums.message_service_type import MessageServiceType
from pyrogram.types.messages_and_media.message import Message


async def check_pinsremove_func(_, __, msg: Message):
    base = sqlite3.connect("main_base.db")
    cur = base.cursor()
    pins_ids = cur.execute("SELECT * FROM pins").fetchall()
    for pin_id in pins_ids:
        if msg.chat.id == pin_id[0]: # [0] потому что fetchall возвращает список кортежей
            base.close()
            return True
    base.close()
    return False
pinsremove_filter = filters.create(check_pinsremove_func)


async def pinsremove_filter_func(_, msg: Message):
    if msg.service == MessageServiceType.PINNED_MESSAGE:
        await msg.delete()


for a in apps:
    a.add_handler(MessageHandler(pinsremove_filter_func, pinsremove_filter & filters.service & filters.pinned_message))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS pins (id INT PRIMARY KEY)")
base.commit()
base.close()
