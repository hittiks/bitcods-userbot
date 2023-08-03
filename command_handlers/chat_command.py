import time
import config
import asyncio
from tqdm import tqdm
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.raw import functions, types
from pyrogram.client import Client
from pyrogram.handlers import MessageHandler
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram.enums.message_service_type import MessageServiceType
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
    "ru":{
        ".chat": "<code>.chat</code>  —  статистика сообщений в чате или лс\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - режим отображения результатов: строго 0 или 1, где 0 - это вывод без \"пустых пунктов\","+
                                " а 1 сответственно - с ними"
    },
    "en": {
        ".chat": "<code>.chat</code>  —  statistics of messages in group or private chat\n"+
                "==============================\n<u>Params</u>:\n"+
                        "    __**First param:**__ (required) - results showing mode: strictly 0 or 1, where 0 - its showing without \"empty items\","+
                                " and 1 - with it"
    }
}


PHRASES_VAR = {
    "ru": {
        "require_param_as_num": "Требуется параметр в виде числа (строго 0 или 1)",
        "undefined": "Неопределённое сообщение"
    },
    "en": {
        "require_param_as_num": "Require param as a num (strictly 0 or 1)",
        "undefined": "Undefined message"
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


def __try_to_get_attr(obj: object, attr: str, default = None):
    try:
        return obj.__getattribute__(attr)
    except AttributeError:
        return default


async def __get_chat_history_count(cl: Client, chat_id: int):
    r1 = await cl.invoke(
            functions.messages.GetHistory(
                peer=await cl.resolve_peer(chat_id),
                offset_id=0,
                offset_date=0,
                add_offset=0,
                limit=2,
                max_id=0,
                min_id=0,
                hash=0
            )
        )
    
    if isinstance(r1, types.messages.Messages):
        return len(r1.messages)
    elif isinstance(r1, types.messages.MessagesSlice):
        r2 = await cl.invoke(
            functions.messages.GetHistory(
                peer=await cl.resolve_peer(chat_id),
                offset_id=1,
                offset_date=1,
                add_offset=0,
                limit=1,
                max_id=r1.messages[0].id-r1.count,
                min_id=0,
                hash=0
            )
        )

        if r2.offset_id_offset:
            return r1.count + r2.offset_id_offset
        else:
            return r1.count
    else:
        return r1.count


async def chat_command_func(cl: Client, msg: Message):
    await msg.delete()

    start_time = time.time()

    try:
        mode = int(msg.text.split(" ")[1])
        if mode not in [0, 1]:
            raise ValueError
    except (IndexError, ValueError):
        await send_temp_message(cl, msg.chat.id, get_phrase("require_param_as_num"))
        return

    data = {
        "all (counted by me)": 0,
        "all (counted by tg)": {
            "_": 0,
            "sum": {
                "_": 0,
                "text": {
                    "_": 0,
                    "url": 0,
                },
                "media": {
                    "_": 0,
                    "live secret photo": 0,
                    "live secret video": 0,
                    "media invoice": 0,
                    "invoice": 0,
                    "geo live": 0,
                    "unsupported": 0,
                    MessageMediaType.PHOTO: 0,
                    MessageMediaType.VIDEO: 0,
                    MessageMediaType.AUDIO: 0,
                    MessageMediaType.VOICE: 0,
                    MessageMediaType.STICKER: 0,
                    MessageMediaType.VIDEO_NOTE: 0,
                    MessageMediaType.ANIMATION: 0,
                    MessageMediaType.DOCUMENT: 0,
                    MessageMediaType.POLL: 0,
                    MessageMediaType.DICE: 0,
                    MessageMediaType.LOCATION: 0,
                    MessageMediaType.VENUE: 0,
                    MessageMediaType.CONTACT: 0,
                    MessageMediaType.WEB_PAGE: 0,
                    MessageMediaType.GAME: 0,
                },
                "service": {
                    "_": 0,
                    "die secret photo": 0,
                    "die secret video": 0,
                    "new chat video": 0,
                    "set chat theme": 0,
                    "off chat theme": 0,
                    "call missed": 0,
                    "call hang up": 0,
                    "call busy": 0,
                    "contact sign up": 0,
                    "screenshot taken": 0,
                    "set messages autodelete": 0,
                    "off messages autodelete": 0,
                    "game high score": 0,
                    "suggest profile photo": 0,
                    "bot allowed": 0,
                    "payment sent": 0,
                    "payment sent me": 0,
                    "requested user": 0,
                    "requested chat/channel": 0,
                    "web view data sent": 0,
                    "web view data sent me": 0,
                    MessageServiceType.PINNED_MESSAGE: 0,
                    MessageServiceType.NEW_CHAT_MEMBERS: 0,
                    MessageServiceType.LEFT_CHAT_MEMBERS: 0,
                    MessageServiceType.VIDEO_CHAT_SCHEDULED: 0,
                    MessageServiceType.VIDEO_CHAT_STARTED: 0,
                    MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED: 0,
                    MessageServiceType.VIDEO_CHAT_ENDED: 0,
                    MessageServiceType.NEW_CHAT_PHOTO: 0,
                    MessageServiceType.DELETE_CHAT_PHOTO: 0,
                    MessageServiceType.NEW_CHAT_TITLE: 0,
                    MessageServiceType.GROUP_CHAT_CREATED: 0,
                    MessageServiceType.MIGRATE_FROM_CHAT_ID: 0,
                    MessageServiceType.MIGRATE_TO_CHAT_ID: 0,
                    MessageServiceType.WEB_APP_DATA: 0,
                },
            },
            "undefined": 0,
        },
    }

    data["all (counted by tg)"]["_"] = await __get_chat_history_count(cl, msg.chat.id) # cl.get_chat_history_count(msg.chat.id)
    sum = data["all (counted by tg)"]["sum"]
    pbar = tqdm(desc="Not deleted messages", total=data["all (counted by tg)"]["_"])
    async for x in cl.get_chat_history(chat_id=msg.chat.id):
        pbar.update()
        try:
            data["all (counted by me)"]+=1
            list1: Message = x
            if list1.text:
                sum["text"]["_"]+=1
                if list1.entities:
                    for y in list1.entities:
                        if y.type==MessageEntityType.URL or (y.type==MessageEntityType.TEXT_LINK and list1.media!=MessageMediaType.WEB_PAGE):
                            sum["text"]["url"]+=1
            elif list1.media:
                sum["media"]["_"]+=1
                if list1.media==MessageMediaType.PHOTO and list1.photo and list1.photo.ttl_seconds:
                    sum["media"]["live secret photo"]+=1
                elif list1.media==MessageMediaType.PHOTO and not list1.photo:
                    sum["media"]["_"]-=1
                    sum["service"]["_"]+=1
                    sum["service"]["die secret photo"]+=1
                elif list1.media==MessageMediaType.VIDEO and list1.video and list1.video.ttl_seconds:
                    sum["media"]["live secret video"]+=1
                elif list1.media==MessageMediaType.VIDEO and not list1.video:
                    sum["media"]["_"]-=1
                    sum["service"]["_"]+=1
                    sum["service"]["die secret video"]+=1
                else:
                    sum["media"][list1.media]+=1
            elif list1.service:
                sum["service"]["_"]+=1
                m = (await __gm(cl, msg.chat.id, list1.id)).messages[0]
                if list1.service==MessageServiceType.NEW_CHAT_PHOTO and __try_to_get_attr(__try_to_get_attr(__try_to_get_attr(m, "action"), "photo"), "video_sizes"):
                    sum["service"]["new chat video"]+=1
                else:
                    sum["service"][list1.service]+=1
            else:
                m = (await __gm(cl, list1.chat.id, list1.id)).messages[0]
                if isinstance(__try_to_get_attr(m, "action"), types.MessageActionSetChatTheme):
                    sum["service"]["_"]+=1
                    if m.action.emoticon != "":
                        sum["service"]["set chat theme"]+=1
                    else:
                        sum["service"]["off chat theme"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionPhoneCall):
                    sum["service"]["_"]+=1
                    if isinstance(m.action.reason, types.PhoneCallDiscardReasonMissed):
                        sum["service"]["call missed"]+=1
                    elif isinstance(m.action.reason, types.PhoneCallDiscardReasonHangup):
                        sum["service"]["call hang up"]+=1
                    elif isinstance(m.action.reason, types.PhoneCallDiscardReasonBusy):
                        sum["service"]["call busy"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionContactSignUp):
                    sum["service"]["_"]+=1
                    sum["service"]["contact sign up"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionScreenshotTaken):
                    sum["service"]["_"]+=1
                    sum["service"]["screenshot taken"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionSetMessagesTTL):
                    sum["service"]["_"]+=1
                    if m.action.period != 0:
                        sum["service"]["set messages autodelete"]+=1
                    else:
                        sum["service"]["off messages autodelete"]+=1
                elif list1.game_high_score:
                    sum["service"]["_"]+=1
                    sum["service"]["game high score"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionSuggestProfilePhoto):
                    sum["service"]["_"]+=1
                    sum["service"]["suggest profile photo"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionBotAllowed):
                    sum["service"]["_"]+=1
                    sum["service"]["bot allowed"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionPaymentSent):
                    sum["service"]["_"]+=1
                    sum["service"]["payment sent"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionPaymentSentMe):
                    sum["service"]["_"]+=1
                    sum["service"]["payment sent me"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionRequestedPeer) and isinstance(__try_to_get_attr(m.action, "peer"), types.PeerUser):
                    sum["service"]["_"]+=1
                    sum["service"]["requested user"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionRequestedPeer):
                    sum["service"]["_"]+=1
                    sum["service"]["requested chat/channel"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionWebViewDataSent):
                    sum["service"]["_"]+=1
                    sum["service"]["web view data sent"]+=1
                elif isinstance(__try_to_get_attr(m, "action"), types.MessageActionWebViewDataSentMe):
                    sum["service"]["_"]+=1
                    sum["service"]["web view data sent me"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaInvoice) and __try_to_get_attr(m.media, "extended_media"):
                    sum["media"]["_"]+=1
                    sum["media"]["media invoice"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaInvoice):
                    sum["media"]["_"]+=1
                    sum["media"]["invoice"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaGeoLive):
                    sum["media"]["_"]+=1
                    sum["media"]["geo live"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaDocument) and __try_to_get_attr(m.media, "ttl_seconds"):
                    sum["service"]["_"]+=1
                    sum["service"]["die secret video"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaUnsupported):
                    sum["media"]["_"]+=1
                    sum["media"]["unsupported"]+=1
                else:
                    data["all (counted by tg)"]["undefined"]+=1
                    await cl.send_message(msg.chat.id, get_phrase("undefined"), reply_to_message_id=list1.id)
        except Exception as e:
            log(f"----------'CHAT' HAVE GOT ERROR: {e}----------", LogMode.ERROR)
        await asyncio.sleep(0.01)
    pbar.close()
    sum["_"] = sum["text"]["_"] + sum["media"]["_"] + sum["service"]["_"]

    def pretty(data: dict, tab=""):
        s = ""
        for k,v in data.items():
            if k == '_': continue
            if isinstance(v, dict):
                s += f"{tab}{k}: {v['_']}\n"
                s += pretty(v, tab + "|   ")
            else:
                if v or mode:
                    if isinstance(k, str):
                        s += f"{tab}{k}: {v}\n"
                    else:
                        k: MessageServiceType
                        s += f"{tab}{' '.join(k.name.lower().split('_'))}: {v}\n"
        return s

    await cl.send_message(msg.chat.id, pretty(data).strip() + f"\n\nTime to count: {time.time() - start_time:.2f} s")


for a in apps:
    a.add_handler(MessageHandler(chat_command_func, filters.command("chat", prefixes=".") & filters.user("me")))
