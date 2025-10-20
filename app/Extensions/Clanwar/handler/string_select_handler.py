from interactions import (
    ChannelSelectMenu,
    ChannelType,
    ActionRow,
    UserSelectMenu,
    ComponentContext,
)
from Extensions.Clanwar.model import ClanwarBase
from common import var


async def on_string_select(ctx: ComponentContext, _):
    author = ctx.author
    message = ctx.message
    custom_id = ctx.custom_id
    party = ClanwarBase(_, ctx=ctx)
    await party.get_party(message=message)
    if author.id != party.owner.id and author.id not in var.devs:
        await ctx.send(_("clanwar_only_owner_area"), ephemeral=True, delete_after=5)
        return
    if custom_id.endswith("party"):
        value = ctx.values[0]
        match value:
            case "edit_voicechannel":
                select = ChannelSelectMenu(
                    custom_id=f"party_voicechannel_{party.partyid}",
                    placeholder=_("common_select_voicechannel"),
                    channel_types=[ChannelType.GUILD_VOICE],
                )
                await ctx.send(
                    _("common_select_channel"),
                    components=[ActionRow(select)],
                    ephemeral=True,
                    delete_after=60,
                )
                return
            case "add_thread":
                if await party.add_thread():
                    await ctx.send(
                        _("clanwar_thread_added"), ephemeral=True, delete_after=5
                    )
                else:
                    await ctx.send(
                        _("clanwar_thread_exist"), ephemeral=True, delete_after=5
                    )
                return
            case "delete_thread":
                if await party.del_thread():
                    await ctx.send(
                        _("clanwar_thread_deleted"), ephemeral=True, delete_after=5
                    )
                else:
                    await ctx.send(
                        _("clanwar_no_thread"), ephemeral=True, delete_after=5
                    )
                return
            case "delete":
                await party.delete()
                await ctx.send(_("clanwar_deleted"), ephemeral=True, delete_after=5)
                return
            case "end":
                await party.end_party()
                await ctx.send(_("clanwar_ended"), ephemeral=True, delete_after=5)
                return

            case "start":
                await party.start_party()
                await ctx.send(_("clanwar_started"), ephemeral=True, delete_after=5)
                return

            case "changeowner":
                select = UserSelectMenu(
                    custom_id=f"party_changeowner_{party.partyid}",
                    placeholder=_("clanwar_select_owner"),
                )
                await ctx.send(
                    _("clanwar_select_owner"),
                    components=[ActionRow(select)],
                    ephemeral=True,
                    delete_after=60,
                )
                return
