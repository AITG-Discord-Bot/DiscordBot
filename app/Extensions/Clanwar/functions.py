from interactions import Client

from Extensions.Clanwar.exceptions import StaleClanwarError
from Extensions.Clanwar.model import ClanwarBase


async def _run_for_parties(bot: Client, params, action):
    for idx in params:
        try:
            clanwar = ClanwarBase(bot=bot)
            await clanwar.get_party(partyid=idx)
            await action(clanwar)
        except StaleClanwarError:
            continue


async def notify_clanwar(bot: Client, params):
    await _run_for_parties(bot, params, lambda c: c.notify())


async def finish_clanwar(bot: Client, params):
    await _run_for_parties(bot, params, lambda c: c.end_party())


async def cancel_clanwar(bot: Client, params):
    await _run_for_parties(bot, params, lambda c: c.send_cancel_notification())
