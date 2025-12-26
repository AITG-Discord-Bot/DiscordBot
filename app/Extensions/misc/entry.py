import asyncio
import importlib

from interactions import *
from . import core
from .handler import on_button
from interactions.api.events import Component, BaseVoiceEvent
from common import MyFunctions, options
from common.checks import is_admin
from common.localization import getname, localize, getdesc


class Misc(Extension):
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    # ==============================================
    # CONTEXT MENUS
    # ==============================================
    @message_context_menu(name=getname("app_send_to_channel"))
    @check(is_admin)
    @localize()
    async def send_to_channel(self, ctx: ContextMenuContext, _):
        return await core.send_to_channel(ctx, _)

    @message_context_menu(name=getname("app_set_ticket"))
    @check(is_admin)
    @localize()
    async def set_ticket(self, ctx: ContextMenuContext, _):
        return await core.set_ticket(ctx, _)

    @message_context_menu(name=getname("app_set_reaction_role"))
    @check(is_admin)
    @localize()
    async def set_reaction_role(self, ctx: ContextMenuContext, _):
        return await core.set_reaction_role(ctx, _)

    # ==============================================
    # SLASH COMMANDS
    # ==============================================
    @slash_command(
        name=getname("misc_command_send_embed"),
        description=getdesc("misc_command_send_embed_desc"),
    )
    @check(is_admin)
    @localize()
    async def send_embed(self, ctx: SlashContext, _):
        """임베드 전송법 가이드 명령어, 실제 전송은 버튼으로 합니다."""
        return await core.send_embed(ctx, _)

    @slash_command(
        name=getname("misc_command_move_all"),
        description=getdesc("misc_command_move_all_desc"),
    )
    @options.voicechannel()
    @check(is_admin)
    @localize()
    async def move_all(
        self, ctx: SlashContext, _, options_voicechannel: GuildVoice | GuildStageVoice
    ):
        return await core.move_all(ctx, _, options_voicechannel)

    # ==============================================
    # LISTENERS
    # ==============================================
    @listen(Component)
    @localize()
    async def on_component(self, ctx: ComponentContext, _):
        if ctx.component_type == ComponentType.BUTTON:
            return await on_button.handle(ctx, _)
        return None


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    importlib.reload(core)
    functions_ = functions
    Misc(bot)


def teardown():
    # functions_.remove()
    pass
