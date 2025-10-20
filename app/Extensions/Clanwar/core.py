from datetime import datetime, UTC, timedelta
from interactions import *
from interactions.api.events import Component

from .model import ClanwarBase
from common.localization import language_utc_offsets
from .utils import convert_time


async def add_clanwar_(ctx: SlashContext, _):
    locale = ctx.locale
    utc_offset = language_utc_offsets.get(locale, 0)
    now = datetime.now(UTC)
    # clanwar opens at 14:00 UTC
    if now.hour >= 14:
        now = now + timedelta(days=1)
    now = now.replace(hour=14)
    now = now + timedelta(hours=utc_offset)
    now = now.replace(minute=0, second=0, microsecond=0)
    now = now.strftime("%Y-%m-%d %H:00")
    my_modal = Modal(
        ShortText(
            label=_("clanwar_modal_add_time").format(str(utc_offset)),
            custom_id="partytime",
            placeholder="YYYY-MM-DD HH:MM",
            value=now,
            required=True,
        ),
        ParagraphText(
            label=_("clanwar_modal_add_desc"),
            custom_id="partydesc",
            placeholder=_("clanwar_modal_add_desc.placeholder"),
            required=False,
        ),
        ShortText(
            label=_("clanwar_modal_add_BR"),
            custom_id="partybr",
            placeholder=_("clanwar_modal_add_BR_placeholder"),
            required=True,
        ),
        title=_("clanwar_modal_add_title"),
    )
    await ctx.send_modal(modal=my_modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(modal=my_modal, timeout=300)
    await modal_ctx.defer()
    partytime = modal_ctx.responses["partytime"]
    partytime = convert_time(partytime, utc_offset)
    if partytime is None:
        await ctx.send(_("clanwar_wrong_timeformat"), ephemeral=True)
        return
    partydesc = modal_ctx.responses["partydesc"]
    partygame = modal_ctx.responses["partybr"]
    row1 = ActionRow(
        RoleSelectMenu(
            placeholder=_("clanwar_mention_placeholder"), min_values=1, max_values=1
        )
    )
    row2 = ActionRow(
        Button(label=_("clanwar_no_mention_button"), style=ButtonStyle.RED)
    )
    component_msg = await modal_ctx.send(
        _("clanwar_select_mention"),
        components=[row1, row2],
        ephemeral=True,
        delete_after=60,
    )
    component_rsp: Component = await ctx.bot.wait_for_component(
        components=[row1, row2], timeout=60
    )
    component_ctx = component_rsp.ctx
    role = None
    if component_ctx.component_type == 6:
        role = component_ctx.values[0]
    await component_msg.delete()
    party = ClanwarBase(_, bot=ctx.bot)
    await party.create_party(ctx, partydesc, partygame, partytime, role)
