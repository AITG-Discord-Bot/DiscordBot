import asyncio

from interactions import *
from common.core import MyFunctions
from common.discordbot.components import options
from common.guards.checks import is_admin
from common.localization import getname, getdesc, localize
from common.localization.localizer import news_language_codes
from . import core
from .utils import server_func
from .handler import on_member_add
from interactions.api.events import GuildJoin, GuildLeft, MemberAdd

serverbase = SlashCommand(name=getname("server_command_base"))
serversettingbase = serverbase.group(name=getname("common_settings"))


def newslanguage(
    name="options_newslanguage", desc="options_newslanguage_desc", required=True
):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.STRING,
            required=required,
        )(func)

    return wrapper


class Server(core.Extension):
    """Server related commands."""

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        await server_func.initialize_server(self.bot)

    @listen(GuildJoin, delay_until_ready=True)
    async def on_guild_join(self, event: GuildJoin):
        server = event.guild
        await server_func.add_server(server)

    @listen(GuildLeft, delay_until_ready=True)
    async def on_guild_left(self, event: GuildLeft):
        server = event.guild
        await server_func.remove_server(server)

    @listen(MemberAdd, delay_until_ready=True)
    async def on_member_add(self, event: MemberAdd):
        return await on_member_add.handle(event)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setmodrole"),
        sub_cmd_description=getdesc("server_command_setmodrole_desc"),
    )
    @options.role(desc="server_modrole_option_desc")
    @check(is_admin)
    @localize()
    async def set_mod_role(self, ctx: SlashContext, _, options_role: Role):
        return await core.set_mod_role(ctx, _, options_role)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_viewsettings"),
        sub_cmd_description=getdesc("server_command_viewsettings_desc"),
    )
    @options.ephemeral()
    @check(is_admin)
    @localize()
    async def viewsettings(self, ctx: SlashContext, _, options_ephemeral: bool = True):
        return await core.view_settings(ctx, _, options_ephemeral)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setbotmsgchannel"),
        sub_cmd_description=getdesc("server_command_setbotmsgchannel_desc"),
    )
    @options.textchannel(desc="server_botmessagechannel_option_desc")
    @check(is_admin)
    @localize()
    async def set_bot_message_channel(self, ctx: SlashContext, _, options_textchannel):
        return await core.set_bot_message_channel(ctx, _, options_textchannel)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setclanmaterole"),
        sub_cmd_description=getdesc("server_command_setclanmaterole_desc"),
    )
    @options.role(desc="server_clanmaterole_option_desc")
    @check(is_admin)
    @localize()
    async def set_clan_mate_role(self, ctx: SlashContext, _, options_role: Role):
        return await core.set_clanmate_role(ctx, _, options_role)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setnewschannel"),
        sub_cmd_description=getdesc("server_command_setnewschannel_desc"),
    )
    @options.textchannel(desc="server_newschannel_option_desc")
    @check(is_admin)
    @localize()
    async def setnewschannel(self, ctx: SlashContext, _, options_textchannel):
        return await core.set_news_channel(ctx, _, options_textchannel)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setnewslanguage"),
        sub_cmd_description=getdesc("server_command_setnewslanguage_desc"),
    )
    @newslanguage()
    @check(is_admin)
    @localize()
    async def setnewslanguage(self, ctx: SlashContext, _, options_newslanguage: str):
        return await core.set_news_language(ctx, _, options_newslanguage)

    @setnewslanguage.autocomplete("options_newslanguage")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(choices=news_language_codes)

    @serversettingbase.subcommand(
        sub_cmd_name=getname("server_command_setwelcomemessage"),
        sub_cmd_description=getdesc("server_command_setwelcomemessage_desc"),
    )
    @check(is_admin)
    @localize()
    async def setwelcommessage_helper(self, ctx: SlashContext, _):
        return await core.set_welcomemessage_helper(ctx, _)

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
        return await core.set_clan_name(ctx, _)

    @core.message_context_menu(name=getname("server_app_set_welcome_message"))
    @check(is_admin)
    @localize()
    async def set_welcome_message(self, ctx: core.ContextMenuContext, _):
        return await core.set_welcome_message(ctx, _)


functions_: MyFunctions = None


def setup(bot: core.Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    Server(bot)


def teardown():
    # functions_.remove()
    pass
