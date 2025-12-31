import asyncio

from interactions import *
from interactions.api.events import (
    MessageCreate,
    Disconnect,
    MessageUpdate,
    MessageDelete,
)

from common.core import MyFunctions
from common.guards import is_admin
from common.localization import getname, getdesc, localize
from common.discordbot.components.options import category, textchannel
from . import core
from .handler import (
    on_message_create,
    on_message_update,
    on_message_delete,
    func as handler_func,
)

logginggroup = SlashCommand(name=getname("logging_command_base"))


class Logger(Extension):
    def __init__(self, bot: Client):
        self.bot: Client = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        await handler_func.init(self.bot)

    @logginggroup.subcommand(
        sub_cmd_name=getname("common_settings"),
        sub_cmd_description=getdesc("logging_command_setlogchannel_desc"),
    )
    @category(desc="logging_option_category")
    @textchannel(desc="logging_option_textchannel")
    @check(is_admin)
    @localize()
    async def setlogchannel(
        self, ctx: SlashContext, _, options_textchannel, options_category
    ):
        return await core.setlogchannel(ctx, _, options_textchannel, options_category)

    @logginggroup.subcommand(
        sub_cmd_name=getname("common_delete"),
        sub_cmd_description=getdesc("logging_command_dellogchannel_desc"),
    )
    @category(desc="logging_option_category_del")
    @check(is_admin)
    @localize()
    async def dellogchannel(self, ctx: SlashContext, _, options_category):
        return await core.dellogchannel(ctx, _, options_category)

    @listen(MessageCreate)
    async def on_message_create(self, event: MessageCreate):
        await on_message_create.handle(event)

    @listen(MessageUpdate)
    async def on_message_update(self, event: MessageUpdate):
        await on_message_update.handle(event)

    @listen(MessageDelete)
    async def on_message_delete(self, event: MessageDelete):
        await on_message_delete.handle(event)

    @listen(Disconnect)
    async def on_disconnect(self, event: Disconnect):
        await handler_func.teardown()


# setup / teardown
functions_ = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    Logger(bot)


def teardown():
    asyncio.create_task(handler_func.teardown())
    pass
