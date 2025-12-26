import asyncio
import importlib

from interactions import *
from . import core
from common import MyFunctions, options


class Voice(Extension):
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    # ==============================================
    # CONTEXT MENUS
    # ==============================================

    # ==============================================
    # SLASH COMMANDS
    # ==============================================

    # ==============================================
    # LISTENERS
    # ==============================================


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    importlib.reload(core)
    functions_ = functions
    Voice(bot)


def teardown():
    # functions_.remove()
    pass
