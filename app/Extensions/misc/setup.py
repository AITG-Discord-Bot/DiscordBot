import asyncio

from interactions import *

from .core import *

from common import MyFunctions, waitforcomponent
from common.checks import is_admin
from common.localization import getname, localize


class Misc(Extension):
    """Server related commands."""

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    @message_context_menu(name=getname("app_send_to_channel"))
    @check(is_admin)
    @localize()
    async def send_to_channel(self, ctx: ContextMenuContext, _):
        return await send_to_channel_(ctx, _)


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    Misc(bot)


def teardown():
    # functions_.remove()
    pass
