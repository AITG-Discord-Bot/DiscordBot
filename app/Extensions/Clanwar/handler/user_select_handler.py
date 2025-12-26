from interactions import Client, ComponentContext

from Extensions.Clanwar.model import ClanwarBase
from common import var


async def on_user_select(bot: Client, ctx: ComponentContext, _):
    author = ctx.author
    custom_id = ctx.custom_id
    if custom_id.startswith("party_changeowner"):
        party_id = custom_id.split("_")[2]
        party = ClanwarBase(_, bot=bot)
        await party.get_party(partyid=party_id)
        if author.id != party.owner.id and author.id not in var.devs:
            await ctx.send(_("clanwar_only_owner_area"), ephemeral=True, delete_after=5)
            return
        newowner = ctx.values[0]
        newowner = await ctx.guild.fetch_member(newowner)
        await party.change_owner(newowner)
        await ctx.send(_("clanwar_owner_changed"), ephemeral=True, delete_after=5)
