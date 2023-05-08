import config
from utils import send_temp_message
from on_start import apps

from pyrogram import filters
from pyrogram.types import MessageEntity
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.enums.chat_type import ChatType
from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram.types.messages_and_media.message import Message
from pyrogram.types.user_and_chats.chat_member import ChatMember


HELP_VAR = {
    "ru": {
        ".hiddentag": "<code>.hiddentag</code>  —  отправка сообщения, в котором скрыто отмечены участники чата, кроме ботов и самого себя (максимум 50 акков);"+
                        " фактически отметок будет меньше из-за пропускания ботов и себя\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - текст сообщения, которое будет отправлено уже с отметками"
    },
    "en": {
        ".hiddentag": "<code>.hiddentag</code>  —  sending message, in which hidden mentioned members of chat, except bots and self (max 50 accounts);"+
                        " in fact, there will be less mentions because of the skipping of bots and self\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - text of message, that will be send with mentions"
    }
}


PHRASES_VAR = {
    "ru": {
        "forbidden_in_private_chats": "Команда недоступна в личных чатах"
    },
    "en": {
        "forbidden_in_private_chats": "Command is forbidden in private chats"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def hiddentag_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        target_text = msg.text.split(".hiddentag ", 1)[1]
    except:
        target_text = "."
    
    ch = msg.chat
    if ch.type == ChatType.PRIVATE:
        await send_temp_message(cl, msg.chat.id, get_phrase("forbidden_in_private_chats"))
        return


    hidden_symbol = "⁠" #is not empty, just not displayed
    text = ""
    ent = []
    memb = []
    
    max_num_of_tag = min(await cl.get_chat_members_count(msg.chat.id), 50)

    part_of_members: list[ChatMember] = [z async for z in cl.get_chat_members(msg.chat.id, limit=max_num_of_tag)]

    for member in part_of_members:
        try:
            if member.user.is_bot == False and member.user.id != msg.from_user.id:
                memb.append(await cl.get_users(member.user.id))
        except:
            pass

    for x in range(0, len(memb)):
        text += hidden_symbol
        ent.append(MessageEntity(client=cl, type=MessageEntityType.TEXT_MENTION, offset=x, length=1, user=memb[x]))

    text += target_text
    await cl.send_message(msg.chat.id, text, entities=ent)


for a in apps:
    a.add_handler(MessageHandler(hiddentag_command_func, filters.command("hiddentag", prefixes=".") & filters.user("me")))
