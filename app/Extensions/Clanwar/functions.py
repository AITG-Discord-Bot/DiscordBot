from interactions import Client

from Extensions.Clanwar.model import ClanwarBase


async def notify_clanwar(bot: Client, params):
    for idx in params:
        clanwar = ClanwarBase(bot=bot)
        await clanwar.get_party(partyid=idx)
        await clanwar.notify()


async def finish_clanwar(bot: Client, params):
    for idx in params:
        clanwar = ClanwarBase(bot=bot)
        await clanwar.get_party(partyid=idx)
        await clanwar.end_party()


async def cancel_clanwar(bot: Client, params):
    for idx in params:
        clanwar = ClanwarBase(bot=bot)
        await clanwar.get_party(partyid=idx)
        await clanwar.send_cancel_notification()
