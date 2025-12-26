import interactions.api.events as Events
from interactions import Guild, Member
from common import apirequest
from ..model import ClanwarBase


async def on_member_remove(event: Events.MemberRemove):
    bot = event.bot
    if not bot.is_ready:
        return
    server: Guild = event.guild
    user: Member = event.member
    try:
        results = await apirequest(
            f"/clanwar/server/{server.id}/people/{user.id}", method="GET"
        )
    except Exception:
        return
    for result in results:
        clanwar = ClanwarBase(bot=bot)
        await clanwar.get_party(partyid=result.get("idx"))
        await clanwar.remove_people(user)
        await clanwar.edit_embed(save=False)
