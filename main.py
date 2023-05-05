import asyncio
import logging
import event_handlers
import command_handlers
from on_start import apps
from logger.logger import log, LogMode

from pyrogram.methods.utilities.idle import idle
from pyrogram.dispatcher import Dispatcher
from patch_dispatcher import PatchedDispatcher
Dispatcher.handler_worker = PatchedDispatcher.handler_worker


async def start_bot():
    for a in apps:
        await a.start()

    log("----------USERBOT STARTED----------", LogMode.OK)

    command_handlers.initialize_commands()
    event_handlers.initialize_filters()

    log("----------MODULES INITIALIZED----------", LogMode.OK)


async def stop_bot():
    for a in apps:
        await a.stop(block=True)

    log("----------USERBOT STOPED CORRECTLY----------", LogMode.OK)


async def main():
    try:
        await start_bot()
        logging.getLogger().setLevel(100)
        await idle()
        await stop_bot()
    except KeyboardInterrupt:
        log("----------USERBOT STOPED MANUALLY LOCAL----------", LogMode.OK)
    else:
        log("----------USERBOT STOPED----------", LogMode.OK)
    finally:
        log("----------USERBOT CLOSED----------", LogMode.OK)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    run = loop.run_until_complete

    try:
        run(main())
    except KeyboardInterrupt:
        log("----------USERBOT STOPED MANUALLY GLOBAL----------", LogMode.OK)
