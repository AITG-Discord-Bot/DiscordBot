from interactions import Client, ComponentContext

from Extensions.Clanwar.model import ClanwarBase
from common.core import var


async def on_channel_select(bot: Client, ctx: ComponentContext, _):
    author = ctx.author
    custom_id = ctx.custom_id
    if custom_id.startswith("party_voicechannel"):
        party_id = custom_id.split("_")[2]
        party = ClanwarBase(_, bot=bot)
        await party.get_party(partyid=party_id)
        if author.id != party.owner.id and author.id not in var.devs:
            await ctx.send(_("clanwar_only_owner_area"), ephemeral=True, delete_after=5)
            return
        voicechannel = ctx.values[0]
        url = f"https://discord.com/channels/{ctx.guild.id}/{voicechannel.id}"
        await ctx.send(
            _("clanwar_voicechannel_set").format(url),
            ephemeral=True,
            delete_after=5,
        )
        party.set_voicechannel(voicechannel)
        await party.edit_embed()
        # from here
