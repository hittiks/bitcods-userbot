import api_config
from pyrogram.client import Client
from pyrogram.dispatcher import Dispatcher
from patch_dispatcher import PatchedDispatcher
Dispatcher.handler_worker = PatchedDispatcher.handler_worker


app = Client("my_account", api_id=api_config.API_ID, api_hash=api_config.API_HASH)

apps = [app]
