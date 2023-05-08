import config
import asyncio
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.types import MessageEntity
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.enums.chat_member_status import ChatMemberStatus
from pyrogram.types.messages_and_media.message import Message
from pyrogram.types.user_and_chats.chat_member import ChatMember
from pyrogram.enums.message_entity_type import MessageEntityType


HELP_VAR = {
    "ru": {
        ".sendspam": "<code>.sendspam</code>  —  отправка спам-сообщения, в котором скрыто отмечены участники чата, кроме ботов, админов и самого себя (отправляй только в чаты, где ты админ,"+
                        " или друзьям, но учти, что спам это плохо и за это твой аккаунт могут заблокировать)\n"+
                "__**Обязательно отправлять ответом на сообщение со списком айди чатов (каждый айди на новой строке)**__\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - (пишется на новой строке, а не через пробел) число, сколько участников нужно отметить, (должно быть целым: 0 < x <= 50);"+
                                " фактически отметок будет меньше из-за пропускания админов, ботов и себя\n"+
                        "    __**Второй параметр:**__ (обязательно) - (пишется на новой строке, а не через пробел) текст для рассылки, длинной до 4к символов"
    },
    "en": {
        ".sendspam": "<code>.sendspam</code>  —  sending a spam-message, in which hidden mentions of chat members, except bots, admins and self (send only to chats where you are an admin,"+
                        " or to friends, but keep in mind that spamming is bad and your account can get banned)\n"+
                "__**Required to send as a reply to the message with list of chat ids (each id on new line)**__\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - (is written on a new line, not separated by a space) the number of how many members to mention (must be an integer: 0 < x <= 50);"+
                                " in fact, there will be less mentions because of the skipping of admins, bots and self\n"+
                        "    __**Second param:**__ (required) - (is written on a new line, not separated by a space) text for sending with length less than 4k symbols"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_reply": "Команду нужно обязательно отправлять ответом на сообщение со списком айди чатов",
        "first_param_must_be_number": "Первый параметр должен быть целым числом 0 < x <= 50 (с новой строки)",
        "make_text_lesser": "Сделай текст поменьше",
        "require_second_param": "Требуется второй параметр - текст рассылки (с новой строки)",
        "message_too_long": "Сообщение слишком большое. Рассылка остановлена",
        "chat_delete_my_message": "Чат '{0}' удалил сообщение с рассылкой"
    },
    "en": {
        "require_reply": "The command must be sent as a reply to a message with a list of chat ids",
        "first_param_must_be_number": "The first parameter must be an integer 0 < x <= 50 (from the new line)",
        "make_text_lesser": "Make the text lesser",
        "require_second_param": "Require the second parameter - text for sending (from a new line)",
        "message_too_long": "The message is too large. Sending is stopped",
        "chat_delete_my_message": "Chat '{0}' delete spam message"
    }
}


def get_phrase(key: str):
    return PHRASES_VAR.get(config.PHRASES_LANGUAGE, PHRASES_VAR.get("en", {}))[key]


async def sendspam_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        ids = msg.reply_to_message.text.split("\n")
    except:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_reply"))
        return

    try:
        num_of_tag = int(msg.text.split("\n", 2)[1])
        if num_of_tag <= 0 or num_of_tag > 50:
            raise ValueError
    except:
        await send_temp_message(cl, msg.chat.id, get_phrase("first_param_must_be_number"))
        return
    
    try:
        spam_text = msg.text.split("\n", 2)[2]
        if len(spam_text) > 4000:
            await send_temp_message(cl, msg.chat.id, get_phrase("make_text_lesser"))
            return
    except:
        await send_temp_message(cl, msg.chat.id, get_phrase("require_second_param"))
        return

    sended_messages: list[Message] = []

    for index, id in enumerate(ids):
        hidden_symbol = "⁠"
        text = ""
        chat_numerator = f"({index+1}/{len(ids)})"
        try:
            number_of_all_members = await cl.get_chat_members_count(id)
        except exceptions.not_acceptable_406.ChannelPrivate:
            log(chat_numerator + f"----------CHAT '{id}' IS NOT ACCEPTABLE----------", LogMode.ERROR)
            continue
        except ValueError as e:
            if e.args[0] == f'The chat_id "{id}" belongs to a user':
                log(chat_numerator + f"----------CHAT '{id}' IS PRIVATE----------", LogMode.ERROR)
                continue
            raise e

        ent = []
        tagged_users = []
        max_num_of_tag = min(number_of_all_members, num_of_tag)
        log(f"Max num of tag: {max_num_of_tag}", LogMode.INFO)
        
        name = await cl.get_chat(id).title
        try:
            part_of_members: list[ChatMember] = [z async for z in cl.get_chat_members(id, limit=max_num_of_tag)]
            for member in part_of_members:
                if member.status != ChatMemberStatus.OWNER and member.status != ChatMemberStatus.ADMINISTRATOR and member.user.is_bot == False\
                    and member.user.id != msg.from_user.id:
                    tagged_users.append(await cl.get_users(member.user.id))
        except IndexError:
            log(chat_numerator + f"----------INDEX ERROR IN CHAT '{name}'----------", LogMode.ERROR)
        except exceptions.bad_request_400.ChatAdminRequired:
            log(chat_numerator + f"----------CHAT '{name}' ADMIN REQUIRED (MAYBE CHAT IS CHANNEL)----------", LogMode.ERROR)
            continue
        except exceptions.bad_request_400.ChannelPrivate:
            log(chat_numerator + f"----------CHAT '{name}' IS PRIVATE----------", LogMode.ERROR)
            continue
        
        for y, tagged_user in enumerate(tagged_users):
            text += hidden_symbol
            ent.append(MessageEntity(client=cl, type=MessageEntityType.TEXT_MENTION, offset=y, length=1, user=tagged_user))

        text += spam_text
        try:
            sended_messages.append(await cl.send_message(id, text, entities=ent))
        except exceptions.bad_request_400.MessageTooLong:
            log("----------MESSAGE TOO LONG----------", LogMode.INFO)
            await cl.send_message(msg.chat.id, get_phrase("message_too_long"))
            break
        except exceptions.bad_request_400.ChatRestricted:
            log(chat_numerator + f"----------CHAT '{name}' RESTRICTED----------", LogMode.ERROR)
        except exceptions.bad_request_400.ChatAdminRequired:
            log(chat_numerator + f"----------CHAT '{name}' ADMIN REQUIRED (MAYBE CHAT IS CHANNEL)----------", LogMode.ERROR)
        except exceptions.flood_420.SlowmodeWait:
            log(chat_numerator + f"----------CHAT '{name}' HAVE SLOWMODE----------", LogMode.ERROR)
        except exceptions.forbidden_403.ChatWriteForbidden:
            log(chat_numerator + f"----------CAN NOT WRITE IN CHAT '{name}'----------", LogMode.ERROR)
        except exceptions.bad_request_400.UserBannedInChannel:
            log(chat_numerator + f"----------USER BANNED IN CHAT '{name}'----------", LogMode.ERROR)
        else:
            log(chat_numerator + f"----------CHAT '{name}' HAVE GOT MY MESSAGE----------", LogMode.INFO)
    log("----------MESSAGES SENDED----------", LogMode.INFO)
    
    await asyncio.sleep(1)

    for index, mess in enumerate(sended_messages):
        if await cl.get_messages(mess.chat.id, mess.id).empty == True:
            log(f"({index+1}/{len(sended_messages)})----------CHAT '{mess.chat.title}' DELETE MY MESSAGE----------", LogMode.ERROR)
            await cl.send_message(msg.chat.id, get_phrase("chat_delete_my_message").format(mess.chat.title))
    log("----------ALL DONE----------", LogMode.OK)


for a in apps:
    a.add_handler(MessageHandler(sendspam_command_func, filters.command("sendspam", prefixes=".") & filters.user("me")))
