import asyncio

from interactions import *
import common.options as options
from common import MyFunctions
from common.checks import is_admin
from common.localization import getname, getdesc, localize
from .core import *

serverbase = SlashCommand(name=getname("server_command_base"))
serversettingbase = serverbase.group(name=getname("common_settings"))


class Server(Extension):
    """Server related commands."""

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setmodrole"),
        sub_cmd_description=getdesc("server_command_setmodrole_desc"),
    )
    @options.role(desc="server_modrole_option_desc")
    @check(is_admin)
    @localize()
    async def set_mod_role(self, ctx: SlashContext, _, options_role: Role):
        return await set_mod_role_(ctx, _, options_role)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_viewsettings"),
        sub_cmd_description=getdesc("server_command_viewsettings_desc"),
    )
    @check(is_admin)
    @localize()
    async def viewsettings(self, ctx: SlashContext, _):
        return await view_settings_(ctx, _)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setbotmsgchannel"),
        sub_cmd_description=getdesc("server_command_setbotmsgchannel_desc"),
    )
    @options.textchannel(desc="server_botmessagechannel_option_desc")
    @check(is_admin)
    @localize()
    async def set_bot_message_channel(self, ctx: SlashContext, _, options_textchannel):
        return await set_bot_message_channel_(ctx, _, options_textchannel)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setclanmaterole"),
        sub_cmd_description=getdesc("server_command_setclanmaterole_desc"),
    )
    @options.role(desc="server_clanmaterole_option_desc")
    @check(is_admin)
    @localize()
    async def set_clan_mate_role(self, ctx: SlashContext, _, options_role: Role):
        return await set_clanmate_role_(ctx, _, options_role)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setnewschannel"),
        sub_cmd_description=getdesc("server_command_setnewschannel_desc"),
    )
    @options.textchannel(desc="server_newschannel_option_desc")
    @check(is_admin)
    @localize()
    async def setnewschannel(self, ctx: SlashContext, _, options_textchannel):
        return await set_news_channel_(ctx, _, options_textchannel)

    # @serversettingbase.subcommand(
    #     sub_cmd_name=getname("server_command_setlinkrole"),
    #     sub_cmd_description=getdesc("server_command_setlinkrole_desc"),
    # )
    # @options.role(desc="server_linkrole_option_desc")
    # @check(is_admin)
    # @localize()
    # async def setlinkrole(self, ctx: SlashContext, _, options_role: Role):
    #     return await set_link_role_(ctx, _, options_role)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setclanname"),
        sub_cmd_description=getdesc("server_command_setclanname_desc"),
    )
    @check(is_admin)
    @localize()
    async def set_clan_name(self, ctx: SlashContext, _):
        return await set_clan_name_(ctx, _)

    @message_context_menu(name=getname("server_app_set_welcome_message"))
    @check(is_admin)
    @localize()
    async def set_welcome_message(self, ctx: ContextMenuContext, _):
        return await set_welcome_message_(ctx, _)


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    Server(bot)


def teardown():
    # functions_.remove()
    pass
