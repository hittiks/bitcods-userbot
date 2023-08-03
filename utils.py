import asyncio
from pyrogram.client import Client


async def send_temp_message(cl: Client, chat_id: int, text: str, pause: int = 3):
    mess = await cl.send_message(chat_id, text)
    await asyncio.sleep(pause)
    await mess.delete()
