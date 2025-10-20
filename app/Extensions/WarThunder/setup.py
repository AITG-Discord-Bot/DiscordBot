from interactions import SlashCommand, Extension, check, Client

from common.localization import localize, getname, getdesc
from common import is_admin, options, MyFunctions

from .core import *
from .functions import *

notify_vacation_end_name = "notify_vacation_end"

wtbase = SlashCommand(name=getname("wt_command_base"))
squadronbase = wtbase.group(name=getname("wt_squadron_command_base"))


class WarThunder(Extension):
    def __init__(self, bot: Client):
        self.bot = bot

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_check_clanmate"),
        sub_cmd_description=getdesc("wt_squadron_check_clanmate"),
    )
    @check(is_admin)
    @localize()
    async def check_clanmate(self, ctx: SlashContext, _):
        await check_clanmate_core(ctx, _)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_check_activity"),
        sub_cmd_description=getdesc("wt_squadron_check_activity_desc"),
    )
    @options.integer(desc="wt_squadron_activity_threshold", required=False)
    @options.ephemeral()
    @localize()
    async def check_activity(
        self,
        ctx: SlashContext,
        _,
        options_integer: int = 9999999,
        options_ephemeral: bool = True,
    ):
        await check_activity_core(ctx, _, options_integer, options_ephemeral)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_add_vacation"),
        sub_cmd_description=getdesc("wt_squadron_add_vacation_desc"),
    )
    @options.member(desc="wt_squadron_add_vacation_for", required=False)
    @localize()
    async def add_vacation(self, ctx: SlashContext, _, options_member: Member = None):
        await add_vacation_core(ctx, _, options_member)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_view_vacation"),
        sub_cmd_description=getdesc("wt_squadron_view_vacation_desc"),
    )
    @check(is_admin)
    @localize()
    async def view_vacation(self, ctx: SlashContext, _):
        await view_vacation_core(ctx, _)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_remove_vacation"),
        sub_cmd_description=getdesc("wt_squadron_remove_vacation_desc"),
    )
    @options.member(desc="wt_squadron_remove_vacation_for", required=False)
    @localize()
    async def remove_vacation(
        self, ctx: SlashContext, _, options_member: Member = None
    ):
        await remove_vacation_core(ctx, _, options_member)


# setup / teardown
functions_ = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    functions_.set(notify_vacation_end_name, notify_vacation_end)
    WarThunder(bot)


def teardown():
    # 필요 시 functions_.remove() 구현
    pass
