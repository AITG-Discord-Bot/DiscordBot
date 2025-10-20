import interactions.api.events as Events

from common import MyFunctions, apirequest, RateLimiter
from common.localization import (
    getname,
    getdesc,
    localize,
)
from .core import *
from .functions import notify_clanwar, finish_clanwar, cancel_clanwar
from .handler import on_button, on_string_select, on_channel_select, on_user_select

notify_clanwar_url = "clanwar_notify"
finish_clanwar_url = "clanwar_finish"
cancel_clanwar_url = "clanwar_cancel_notify"
clanwarbase = SlashCommand(name=getname("clanwar_command_base"))


class Clanwar(Extension):
    def __init__(self, bot: Client):
        self.bot = bot
        self.ratelimiter = RateLimiter(max_calls=2, period=60)

    @clanwarbase.subcommand(
        sub_cmd_name=getname("clanwar_command_add"),
        sub_cmd_description=getdesc("clanwar_command_add_desc"),
    )
    @localize()
    async def add_clanwar(self, ctx: SlashContext, _):
        return await add_clanwar_(ctx, _)

    @listen(Events.Component)
    @localize(server_only=False)
    async def on_component(self, ctx: ComponentContext, _):
        if ctx.component_type == ComponentType.BUTTON:
            return await on_button(self.ratelimiter, ctx, _)
        elif ctx.component_type == ComponentType.STRING_SELECT:
            return await on_string_select(ctx, _)
        elif ctx.component_type == ComponentType.CHANNEL_SELECT:
            return await on_channel_select(self.bot, ctx, _)
        elif ctx.component_type == ComponentType.USER_SELECT:
            return await on_user_select(self.bot, ctx, _)
        return None

    @listen(Events.MemberRemove, delay_until_ready=True)
    async def on_guild_left(self, event: Events.MemberRemove):
        if not self.bot.is_ready:
            return
        server: Guild = event.guild
        user: Member = event.member
        results = await apirequest(
            f"/clanwar/server/{server.id}/people/{user.id}", method="GET"
        )
        for result in results:
            clanwar = ClanwarBase(bot=self.bot)
            await clanwar.get_party(partyid=result.get("idx"))
            await clanwar.remove_people(user)
            await clanwar.edit_embed(save=False)


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    functions_.set(notify_clanwar_url, notify_clanwar)
    functions_.set(finish_clanwar_url, finish_clanwar)
    functions_.set(cancel_clanwar_url, cancel_clanwar)
    Clanwar(bot)


def teardown():
    functions_.remove(notify_clanwar_url)
