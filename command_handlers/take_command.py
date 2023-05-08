import os
import config
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.errors import exceptions
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".take": "<code>.take</code>  —  получение всей информации о сообщении\n"+
                "__**Обязательно отправлять ответом на целевое сообщение**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (необязательно) - айди целевого чата (первая ситуация), если не указано,"+
                                " то будет использован айди текущего чата (вторая ситуация), а первым параметром можно указать поле сообщения"+
                                " (смотри третий параметр); нужно учитывать, что при копировании ссылки с телеграма айди имеет одинаковый формат"+
                                " для любого чата, а в пирограме нет, соответственно к айди группового чата нужно добавить число 1 000 000 000 000,"+
                                " а к айди супергруппы или канала добавить то же число и дописать минус в начале; личные чаты не меняются\n"+
                        "    __**Второй параметр:**__ (необязательно) - айди целевого сообщения (первая ситуация), если не указано,"+
                                " то будет использован айди сообщения, на которое отвечает сообщение с командой (вторая ситуация), а вторым параметром можно указать"+
                                " поле сообщения (смотри четвёртый параметр)\n"+
                        "    __**Третий параметр:**__ (необязательно) - конкретное поле (часть) объекта сообщения, которую требуется получить, например поле from_user;"+
                                " если введённое поле отсутствует у объекта сообщения, то будет выведен весь объект\n"+
                        "    __**Четвёртый параметр:**__ (необязательно) - как предыдущий параметр, только применяется не ко всему сообщению, а к той его части, которая"+
                                " была получена с помощью предыдущего параметра; если введённое поле отсутствует у данной части сообщения, то будет выведено вся часть"
    },
    "en": {
        ".take": "<code>.take</code>  —  получение всей информации о сообщении\n"+
                "__**Required to send as a reply to the target message**__\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (not required) - id of target chat (first situation), if not set, than will use id of current chat"+
                                " (second situation), and the first param can be field of message (see third param); need to consider, that when copying"+
                                " a link from Telegram id has the same format for any chat, but in the program does not, so you need to add a number"+
                                " 1 000 000 000 000 to the group chat id, and add the same number to the supergroup or channel id and add a minus in the beginning;"+
                                " private chats don't change\n"+
                        "    __**Second param:**__ (not required) - id of target message (first situation), if not set, than will use id of message,"+
                                " on which reply message with command (second situation), and the second param can be field of message (see fourth param)\n"+
                        "    __**Third param:**__ (not required) - concrete field (part) of message object, that you need to get, for example field from_user;"+
                                " if the entered field is missing from the message object, the whole object will be displayed\n"+
                        "    __**Fourth param:**__ (not required) - as the previous param, but it does not apply to the whole message, it apply to the part of message,"+
                                " which was obtained using the previous param; if the entered field is missing from the given part of the message,"+
                                " the whole part will be displayed"
    }
}


PHRASES_VAR = {
    "ru": {
        "incorect_use": "Неправильное использование команды",
        "message_too_long": "Сообщение слишком большое"
    },
    "en": {
        "incorect_use": "Incorect use of command",
        "message_too_long": "Message too long"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def take_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    target1 = ""
    target2 = ""

    try:
        ch_id = int(msg.text.split()[1])
        msg_id = int(msg.text.split()[2])
        try:
            target1 = msg.text.split()[3]
            target2 = msg.text.split()[4]
        except:
            pass
    except:
        try:
            ch_id = msg.chat.id
            msg_id = msg.reply_to_message.id
            try:
                target1 = msg.text.split()[1]
                target2 = msg.text.split()[2]
            except:
                pass
        except:
            await send_temp_message(cl, msg.chat.id, get_phrase("incorect_use"))
            return
    
    message = await cl.get_messages(ch_id, msg_id)
    try:
        try:
            log(str(message.__dict__[target1].__dict__[target2]), LogMode.INFO)
            await cl.send_message(msg.chat.id, message.__dict__[target1].__dict__[target2])
        except (KeyError, AttributeError):
            try:
                log(str(message.__dict__[target1]), LogMode.INFO)
                await cl.send_message(msg.chat.id, message.__dict__[target1])
            except KeyError:
                log(str(message), LogMode.INFO)
                await cl.send_message(msg.chat.id, message)
    except exceptions.bad_request_400.MessageTooLong:
        log("----------MESSAGE TOO LONG----------", LogMode.ERROR)
        await send_temp_message(cl, msg.chat.id, get_phrase("message_too_long"))
        with open(f"message_{message.id}.txt", "w", encoding="utf-8") as f:
            f.write(str(message))
        await cl.send_document(msg.chat.id, f"message_{message.id}.txt")
        try:
            os.remove(f"message_{message.id}.txt")
        except FileNotFoundError:
            pass


for a in apps:
    a.add_handler(MessageHandler(take_command_func, filters.command("take", prefixes=".") & filters.user("me")))
