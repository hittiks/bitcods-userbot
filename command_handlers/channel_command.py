import asyncio
from tqdm import tqdm
from utils import send_temp_message
from on_start import apps
from logger.logger import log, LogMode

from pyrogram import filters
from pyrogram.raw import functions, types
from pyrogram.client import Client
from pyrogram.errors import exceptions
from pyrogram.handlers import MessageHandler
from pyrogram.enums.chat_type import ChatType
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram.enums.message_service_type import MessageServiceType
from pyrogram.types.messages_and_media.message import Message


HELP_VAR = {
        ".channel": "<code>.channel</code>  —  статистика постов в канале по его айди\n"+
                "==============================\n<u>Параметры</u>:\n"+
                        "    __**Первый параметр:**__ (обязательно) - айди целевого канала\n"+
                        "    __**Второй параметр:**__ (обязательно) - режим отображения результатов: строго 0 или 1, где 0 - это вывод без \"пустых пунктов\","+
                        " а 1 сответственно - с ними"
}


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


# Статистика постов в канале по его айди
async def channel_command_func(cl: Client, msg: Message):
    await msg.delete()
    
    try:
        channel_id = int(msg.text.split(" ")[1])
    except (IndexError, ValueError):
        await send_temp_message(cl, msg.chat.id, "Требуется первый параметр в виде числа")
        return

    try:
        mode = int(msg.text.split(" ")[2])
        if mode not in [0, 1]:
            raise ValueError
    except (IndexError, ValueError):
        await send_temp_message(cl, msg.chat.id, "Требуется второй параметр в виде числа (строго 0 или 1)")
        return

    try:
        ch = await cl.get_chat(channel_id)
    except exceptions.bad_request_400.PeerIdInvalid:
        await send_temp_message(cl, msg.chat.id, "Получена ошибка PeerIdInvalid при попытке получить канал")
        return
    except exceptions.bad_request_400.ChannelPrivate:
        await send_temp_message(cl, msg.chat.id, "Канал недоступен из-за приватности")
        return
    else:
        if ch.type != ChatType.CHANNEL:
            await send_temp_message(cl, msg.chat.id, "Айди не принадлежит каналу")
            return


    data = {
        "all posts (id of last)": 0,
        "all posts (counted by tg)": {
            "_": 0,
            "sum": {
                "_": 0,
                "text": {
                    "_": 0,
                    "restricted message": 0,
                    "url": 0,
                },
                "media": {
                    "_": 0,
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
                },
                "service": {
                    "_": 0,
                    "new chat video": 0,
                    "channel will be deleted soon": 0,
                    MessageServiceType.PINNED_MESSAGE: 0,
                    MessageServiceType.VIDEO_CHAT_SCHEDULED: 0,
                    MessageServiceType.VIDEO_CHAT_STARTED: 0,
                    MessageServiceType.VIDEO_CHAT_ENDED: 0,
                    MessageServiceType.NEW_CHAT_PHOTO: 0,
                    MessageServiceType.DELETE_CHAT_PHOTO: 0,
                    MessageServiceType.NEW_CHAT_TITLE: 0,
                    MessageServiceType.CHANNEL_CHAT_CREATED: 0,
                    MessageServiceType.WEB_APP_DATA: 0,
                },
            },
            "undefined": 0,
        },
    }

    data["all posts (id of last)"] = [x async for x in cl.get_chat_history(channel_id, limit=1)][0].id
    data["all posts (counted by tg)"]["_"] = await cl.get_chat_history_count(channel_id)
    sum = data["all posts (counted by tg)"]["sum"]
    pbar = tqdm(desc="Not deleted posts", total=data["all posts (counted by tg)"]["_"])
    async for x in cl.get_chat_history(chat_id=channel_id):
        pbar.update()
        try:
            list1: Message = x
            if list1.text:
                sum["text"]["_"]+=1
                if list1.chat.restrictions:
                    sum["text"]["restricted message"]+=1
                elif list1.entities:
                    for y in list1.entities:
                        if y.type==MessageEntityType.URL or (y.type==MessageEntityType.TEXT_LINK and list1.media!=MessageMediaType.WEB_PAGE):
                            sum["text"]["url"]+=1
            elif list1.media:
                sum["media"]["_"]+=1
                sum["media"][list1.media]+=1
            elif list1.service:
                sum["service"]["_"]+=1
                m = (await __gm(cl, channel_id, list1.id)).messages[0]
                if list1.service==MessageServiceType.NEW_CHAT_PHOTO and __try_to_get_attr(__try_to_get_attr(__try_to_get_attr(m, "action"), "photo"), "video_sizes"):
                    sum["service"]["new chat video"]+=1
                else:
                    sum["service"][list1.service]+=1
            else:
                m = (await __gm(cl, list1.chat.id, list1.id)).messages[0]
                if isinstance(__try_to_get_attr(m, "action"), types.MessageActionCustomAction) and __try_to_get_attr(m.action, "message") and "The account of the user that owns this channel has been inactive" in m.action.message:
                    sum["service"]["_"]+=1
                    sum["service"]["channel will be deleted soon"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaInvoice) and __try_to_get_attr(m.media, "extended_media"):
                    sum["media"]["_"]+=1
                    sum["media"]["media invoice"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaInvoice):
                    sum["media"]["_"]+=1
                    sum["media"]["invoice"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaGeoLive):
                    sum["media"]["_"]+=1
                    sum["media"]["geo live"]+=1
                elif isinstance(__try_to_get_attr(m, "media"), types.MessageMediaUnsupported):
                    sum["media"]["_"]+=1
                    sum["media"]["unsupported"]+=1
                else:
                    data["all posts (counted by tg)"]["undefined"]+=1
                    await cl.send_message(msg.chat.id, f"undefined message with id {list1.id}")
        except Exception as e:
            log(f"----------'CHANNEL' HAVE GOT ERROR: {e}----------", LogMode.ERROR)
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

    await cl.send_message(msg.chat.id, pretty(data).strip())


for a in apps:
    a.add_handler(MessageHandler(channel_command_func, filters.command("channel", prefixes=".") & filters.user("me")))
