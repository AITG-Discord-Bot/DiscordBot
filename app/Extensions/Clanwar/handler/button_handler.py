from interactions import ComponentContext
from Extensions.Clanwar.model import ClanwarBase, PARTYACTIONS
from common import RateLimiter


async def on_button(ratelimiter: RateLimiter, ctx: ComponentContext, _):
    author = ctx.author
    message = ctx.message
    custom_id = ctx.custom_id
    author_id = int(author.id)
    if custom_id.endswith("party"):
        if custom_id.endswith("_cancel_party"):
            partyid = custom_id.split("_")[0]
            party = ClanwarBase(_, ctx=ctx)
            await party.get_party(partyid=partyid)
            if author.id != party.owner.id:
                await ctx.send(
                    _("clanwar_no_owner_area"), ephemeral=True, delete_after=5
                )
                return
            await ctx.defer()
            await party.cancel_party()
            await ctx.edit_origin(components=[])
            await ctx.send(_("clanwar_canceled"), ephemeral=True, delete_after=5)
            return

        if not ratelimiter.get(author_id):
            await ctx.send(
                _("common_ratelimit").format(1, 2), ephemeral=True, delete_after=5
            )
            return

        party = ClanwarBase(_, ctx=ctx)
        await party.get_party(message=message)
        if author.id == party.owner.id:
            await ctx.send(_("clanwar_no_owner_area"), ephemeral=True, delete_after=5)
            return

        if custom_id == "exit_party":
            await party.remove_people(author)
            await party.edit_embed(save=False)
            await ctx.send(_("clanwar_leave"), ephemeral=True, delete_after=5)

        if author.id in party.participant + party.primarywaiter + party.waiter:
            await ctx.send(
                _("clanwar_leave_first"),
                ephemeral=True,
                delete_after=5,
            )
            return

        if custom_id == "join_party":
            result = await party.add_people(author)
            await party.edit_embed(save=False)
            if result == PARTYACTIONS.PRIMARY_PARTY:
                await ctx.send(_("clanwar_wait_party"), ephemeral=True, delete_after=5)
            else:
                await ctx.send(_("clanwar_join_party"), ephemeral=True, delete_after=5)

        elif custom_id == "wait_party":
            await party.add_people(author, wait=True)
            await party.edit_embed(save=False)
            await ctx.send(_("clanwar_pending_party"), ephemeral=True, delete_after=5)
