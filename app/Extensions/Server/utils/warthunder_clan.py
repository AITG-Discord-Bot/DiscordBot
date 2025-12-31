from API import APIRequestError
from API.features.server import serverAPI
from API.features.warthunder import warthunderAPI

async def get_clan_names() -> list[str]:
    """
    Get all registered clan names.
    """
    try:
        return await serverAPI.get_clannames()
    except APIRequestError as e:
        if e.status != 404:
            raise e
        return []


async def verify_clanname(name) -> bool:
    """
    check if clan name is valid (if it is a real clan)
    :param name: name to check
    :return: boolean (valid or not)
    """
    res = await warthunderAPI.clan.verify_name(name)
    return res
