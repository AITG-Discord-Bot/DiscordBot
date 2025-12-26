import importlib

from interactions import *
import interactions.api.events as Events
from common.localization import localize, getname, getdesc
from common import is_admin, options, MyFunctions

from . import core, functions as func
from .options import use_personalrating
from .handler import on_member_remove

notify_vacation_end_name = "notify_vacation_end"
send_warthunder_news = "warthunder_news"

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
        await core.check_clanmate_core(ctx, _)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_check_activity"),
        sub_cmd_description=getdesc("wt_squadron_check_activity_desc"),
    )
    @options.integer(desc="wt_squadron_activity_threshold", required=False)
    @use_personalrating()
    @options.ephemeral()
    @localize()
    async def check_activity(
        self,
        ctx: SlashContext,
        _,
        options_integer: int = 9999999,
        options_use_personalrating: bool = False,
        options_ephemeral: bool = True,
    ):
        await core.check_activity_core(
            ctx, _, options_integer, options_use_personalrating, options_ephemeral
        )

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_add_vacation"),
        sub_cmd_description=getdesc("wt_squadron_add_vacation_desc"),
    )
    @options.member(desc="wt_squadron_add_vacation_for", required=False)
    @localize()
    async def add_vacation(self, ctx: SlashContext, _, options_member: Member = None):
        await core.add_vacation_core(ctx, _, options_member)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_view_vacation"),
        sub_cmd_description=getdesc("wt_squadron_view_vacation_desc"),
    )
    # @check(is_admin)
    @options.ephemeral()
    @localize()
    async def view_vacation(self, ctx: SlashContext, _, options_ephemeral: bool = True):
        await core.view_vacation_core(ctx, _, options_ephemeral)

    @squadronbase.subcommand(
        sub_cmd_name=getname("wt_squadron_remove_vacation"),
        sub_cmd_description=getdesc("wt_squadron_remove_vacation_desc"),
    )
    @options.member(desc="wt_squadron_remove_vacation_for", required=False)
    @localize()
    async def remove_vacation(
        self, ctx: SlashContext, _, options_member: Member = None
    ):
        await core.remove_vacation_core(ctx, _, options_member)

    @listen(Events.MemberRemove, delay_until_ready=True)
    async def on_member_remove_(self, event: Events.MemberRemove):
        await on_member_remove(event)

    @wtbase.subcommand(
        sub_cmd_name=getname("wt_command_latestnews"),
        sub_cmd_description=getdesc("wt_command_latestnews_desc"),
    )
    @check(is_admin)
    @localize()
    async def send_latest_news(self, ctx: SlashContext, _):
        return await core.send_latest_news(ctx, _)


# setup / teardown
functions_ = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    functions_.set(notify_vacation_end_name, func.notify_vacation_end)
    functions_.set(send_warthunder_news, func.send_news)
    importlib.reload(core)
    WarThunder(bot)


def teardown():
    # 필요 시 functions_.remove() 구현
    pass
