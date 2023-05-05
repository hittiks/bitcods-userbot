import sqlite3
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


async def check_bots_ad_func(_, __, msg: Message):
    base = sqlite3.connect("main_base.db")
    cur = base.cursor()
    ads = cur.execute("SELECT * FROM ads").fetchall()
    for ad in ads:
        if (msg.text == ad[0] or msg.caption == ad[0]) and msg.from_user and msg.from_user.is_bot == True:
            base.close()
            return True
    base.close()
    return False
botsad_filter = filters.create(check_bots_ad_func)


async def botsad_filter_func(cl: Client, msg: Message):
    try:
        log(f"spam bot: message id: {msg.id} | first name: '{msg.from_user.first_name}'", LogMode.INFO)
        await msg.delete()
    except Exception as e:
        log(f"----------SPAM BOT MESSAGE DELETER HAVE GOT ERROR: {e}----------", LogMode.ERROR)


for a in apps:
    a.add_handler(MessageHandler(botsad_filter_func, botsad_filter))

base = sqlite3.connect("main_base.db")
base.execute("CREATE TABLE IF NOT EXISTS ads (ad TEXT PRIMARY KEY)")
base.commit()
base.close()
