import time
import config
from utils import send_temp_message
from on_start import apps
from datetime import datetime

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".sendtomorrow": "<code>.sendtomorrow</code>  —  отправка сообщений в отложенные сообщения (полезно для чатов с ботами)\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - сколько минут между отправками сообщений  (пример: 120 - через каждые 2 часа);"+
                                " слишком маленькие значения могут игнорироваться сервером телеграма (пример: 1 - сообщение отправится в чат сразу,"+
                                " а не в отложку на время +1 минута)\n"+
                        "    __**Второй параметр:**__ (обязательно) - сколько сообщений отправить всего (100 максимум)"
    },
    "en": {
        ".sendtomorrow": "<code>.sendtomorrow</code>  —  sending messages to pending messages (useful for chats woth bots)\n"+
                "__**Required to send as a reply to the target message**__\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - how many minutes between sending messages (example: 120 - every 2 hours);"+
                                " too small values can be ignored by the telegram server (example: 1 - the message is sent to the chat immediately"+
                                " not a +1 minute time pending)\n"+
                        "    __**Second param:**__ (required) - how many messages to send in total (100 max)"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_reply": "Команда должна быть ответом на сообщение",
        "incorrect_param": "Не все параметры указаны верно"
    },
    "en": {
        "require_reply": "The command must be a reply to a message",
        "incorrect_param": "Not all params are correct"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def sendtomorrow_command_func(cl: Client, msg: Message):
    await msg.delete()

    if msg.reply_to_message == None:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_reply"))
        return
    
    text = msg.reply_to_message.text

    try:
        timer = int(msg.text.split(maxsplit=2)[1])
        num = int(msg.text.split(maxsplit=2)[2])
        if timer<=0 or num<=0:
            raise ValueError
    except IndexError or ValueError:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorrect_param"))
        return
    
    if num>100:
        num=100

    time_now = int(time.time())
    for x in range(1, num+1):
        await cl.send_message(msg.chat.id, text, schedule_date=datetime.fromtimestamp(time_now+timer*60*x))


for a in apps:
    a.add_handler(MessageHandler(sendtomorrow_command_func, filters.command("sendtomorrow", prefixes=".") & filters.user("me")))
