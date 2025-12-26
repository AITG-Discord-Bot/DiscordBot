from interactions import *

from common import MyFunctions, var, is_dev
from . import core


class Dev(Extension):
    def __init__(self, bot):
        self.bot = bot

    @message_context_menu(name="send_as_notification", scopes=var.dev_servers)
    @check(is_dev)
    async def send_as_notification(self, ctx: ContextMenuContext):
        return await core.send_as_notification(ctx)


functions_ = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    Dev(bot)


def teardown():
    pass
