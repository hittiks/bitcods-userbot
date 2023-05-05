import asyncio
from pyrogram.client import Client


async def send_temp_message(cl: Client, chat_id: int, text: str):
    mess = await cl.send_message(chat_id, text)
    await asyncio.sleep(3)
    await mess.delete()
