import os
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.errors import exceptions
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
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
                        "    __**Третий параметр:**__ (необязательно) - конкретное поле (часть) объекта сообщения, которую требуется получить, например, from_user;"+
                                " если введённое поле отсутствует у объекта сообщения, то будет выведен весь объект\n"+
                        "    __**Четвёртый параметр:**__ (необязательно) - как предыдущий параметр, только применяется не ко всему сообщению, а к той его части, которая"+
                                " была получена с помощью предыдущего параметра; если введённое поле отсутствует у данной части сообщения, то будет выведено всё сообщение"
}


# Получение всей информации о сообщении
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
            await send_temp_message(cl, msg.chat.id, "Неправильное использование команды")
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
        await send_temp_message(cl, msg.chat.id, "Сообщение слишком большое")
        with open(f"message_{message.id}.txt", "w", encoding="utf-8") as f:
            f.write(str(message))
        await cl.send_document(msg.chat.id, f"message_{message.id}.txt")
        try:
            os.remove(f"message_{message.id}.txt")
        except FileNotFoundError:
            pass


for a in apps:
    a.add_handler(MessageHandler(take_command_func, filters.command("take", prefixes=".") & filters.user("me")))
