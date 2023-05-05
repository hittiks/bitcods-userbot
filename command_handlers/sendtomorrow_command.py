import time
from utils import send_temp_message
from on_start import apps
from datetime import datetime

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".sendtomorrow": "<code>.sendtomorrow</code>  —  отправка сообщений в отложку (полезно для всяких ботов)\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - через сколько минут отправлять каждое следующее сообщение (пример: 120 - через каждые 2 часа);"+
                                " слишком маленькие значения игнорируются сервером телеграмма (пример: 1 - сообщение отправится в чат сразу, а не в отложку на время"+
                                " +1 минута)\n"+
                        "    __**Второй параметр:**__ (обязательно) - сколько сообщений отправить всего (100 максимум)"
}


# Отправка сообщений в отложку
async def sendtomorrow_command_func(cl: Client, msg: Message):
    await msg.delete()

    if msg.reply_to_message == None:
        await send_temp_message(cl, msg.chat.id, "Команда должна быть ответом на сообщение")
        return
    
    text = msg.reply_to_message.text

    try:
        timer = int(msg.text.split(maxsplit=2)[1])
        num = int(msg.text.split(maxsplit=2)[2])
        if timer<=0 or num<=0:
            raise ValueError
    except IndexError or ValueError:
        await send_temp_message(cl, msg.chat.id, "Не все параметры указаны верно")
        return
    
    if num>100:
        num=100

    time_now = int(time.time())
    for x in range(1, num+1):
        await cl.send_message(msg.chat.id, text, schedule_date=datetime.fromtimestamp(time_now+timer*60*x))


for a in apps:
    a.add_handler(MessageHandler(sendtomorrow_command_func, filters.command("sendtomorrow", prefixes=".") & filters.user("me")))
