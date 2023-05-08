import os
import config
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.raw import functions, types
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru": {
        ".fullmsg": "<code>.fullmsg</code>  —  получение полного объекта сообщения в \"чистом\" виде\n"+
                "__**В зависимости от варианта использования обязательно отправлять ответом на целевое сообщение или нет**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди целевого чата (первая ситуация); если не указано,"+
                                " то будет использован айди текущего чата (вторая ситуация), а первым параметром нужно указать режим работы команды"+
                                " (смотри третий параметр); нужно учитывать, что при копировании ссылки с телеграма айди имеет одинаковый формат"+
                                " для любого чата, а в программе нет, соответственно к айди группового чата нужно добавить число 1 000 000 000 000,"+
                                " а к айди супергруппы или канала добавить то же число и дописать минус в начале; личные чаты не меняются\n"+
                        "    __**Второй параметр:**__ (необязательно) - айди целевого сообщения (первая ситуация); если не указано,"+
                                " то будет использован айди сообщения, на которое отвечает сообщение с командой (вторая ситуация)\n"+
                        "    __**Третий параметр:**__ (необязательно) - режим работы (первая ситуация): 0 или 1 (где 0 - это отправка только сообщений из апдейта,"+
                                " а 1 - отправка всего апдейта (сообщения, пользователи, чаты))"
    },
    "en": {
        ".fullmsg": "<code>.fullmsg</code>  —  getting full object of message in \"clean\" mode\n"+
                "__**Depending on the target action is necessary to send a command to the target message or not**__\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - id of target chat (first situation); if not set,"+
                                " will use id of current chat (second situation), and in first param you need to specify command working mode"+
                                " (see third param); need to consider, that when copying a link from Telegram id has the same format"+
                                " for any chat, but in the program does not, so you need to add a number 1 000 000 000 000 to the group chat id,"+
                                " and add the same number to the supergroup or channel id and add a minus in the beginning; private chats don't change\n"+
                        "    __**Second param:**__ (not required) - id of target message (first situation); if not set,"+
                                " will use id of message, to which answer message with command (second situation)\n"+
                        "    __**Third param:**__ (not required) - working mode (first situation): 0 or 1 (when 0 - sending only messages from update,"+
                                " and 1 - sending full update (messages, users, chats))"
    }
}


PHRASES_VAR = {
    "ru": {
        "incorrect_use": "Неправильное использование команды",
        "incorrect_mode": "Неправильно указан режим работы команды (укажи 0 или 1)",
        "get_peer_id_invalid": "Получена ошибка PeerIdInvalid (скорее всего такого чата/канала не существует)",
        "message_too_long": "Сообщение слишком большое"
    },
    "en": {
        "incorrect_use": "Incorrect use of command",
        "incorrect_mode": "Incorrect setted working mode of command (set 0 or 1)",
        "get_peer_id_invalid": "Get error PeerIdInvalid (most likely no such chat/channel)",
        "message_too_long": "Message too long"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def __gm(
        cl: Client,
        chat_id: int,
        message_ids: int = None,
        reply_to_message_ids: int = None,
        replies: int = 1
    ):
    
    ids, ids_type = (
        (message_ids, types.InputMessageID) if message_ids
        else (reply_to_message_ids, types.InputMessageReplyTo) if reply_to_message_ids
        else (None, None)
    )

    if ids is None:
        raise ValueError("No argument supplied. Either pass message_ids or reply_to_message_ids")

    peer = await cl.resolve_peer(chat_id)

    is_iterable = not isinstance(ids, int)
    ids = list(ids) if is_iterable else [ids]
    ids = [ids_type(id=i) for i in ids]

    if replies < 0:
        replies = (1 << 31) - 1

    if isinstance(peer, types.InputPeerChannel):
        rpc = functions.channels.GetMessages(channel=peer, id=ids)
    else:
        rpc = functions.messages.GetMessages(id=ids)

    r = await cl.invoke(rpc, sleep_threshold=-1)
    return r


async def fullmsg_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        ch_id = int(msg.text.split()[1])
        msg_id = int(msg.text.split()[2])
        option = int(msg.text.split()[3])
    except:
        try:
            ch_id = msg.chat.id
            msg_id = msg.reply_to_message.id
            option = int(msg.text.split()[1])
        except:
            await send_temp_message(cl, msg.chat.id, get_phrase("incorrect_use"))
            return
    
    if option not in [0, 1]:
        await send_temp_message(cl, msg.chat.id, get_phrase("incorrect_mode"))
        return

    try:
        m = await __gm(cl, ch_id, msg_id)
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, get_phrase("get_peer_id_invalid"))
        return
    
    log(str(m), LogMode.INFO)

    if option == 0:
        messages = m.messages
        for message in messages:
            try:
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
    elif option == 1:
        try:
            await cl.send_message(msg.chat.id, m)
        except exceptions.bad_request_400.MessageTooLong:
            log("----------MESSAGE TOO LONG----------", LogMode.ERROR)
            await send_temp_message(cl, msg.chat.id, get_phrase("message_too_long"))
            with open("all_data_from_response.txt", "w", encoding="utf-8") as f:
                f.write(str(m))
            await cl.send_document(msg.chat.id, "all_data_from_response.txt")
            try:
                os.remove("all_data_from_response.txt")
            except FileNotFoundError:
                pass


for a in apps:
    a.add_handler(MessageHandler(fullmsg_command_func, filters.command("fullmsg", prefixes=".") & filters.user("me")))
