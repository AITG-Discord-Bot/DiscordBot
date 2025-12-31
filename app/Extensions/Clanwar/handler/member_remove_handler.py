import interactions.api.events as Events
from interactions import Guild, Member

from API import APIRequestError
from ..model import ClanwarBase
from API.features.clanwar import clanwarAPI


async def on_member_remove(event: Events.MemberRemove):
    bot = event.bot
    if not bot.is_ready:
        return
    server: Guild = event.guild
    user: Member = event.member
    try:
        results = await clanwarAPI.get_clanwar_by_people(server.id, user.id)
    except APIRequestError as e:
        return
    for result in results:
        clanwar = ClanwarBase(bot=bot)
        await clanwar.get_party(partyid=result.idx)
        await clanwar.remove_people(user)
        await clanwar.edit_embed(save=False)
