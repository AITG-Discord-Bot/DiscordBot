from common import apirequest, APIRequestError


async def get_clan_names() -> list[str]:
    """
    Get all registered clan names.
    """
    try:
        res = await apirequest("/server/clannames")
        return res["clannames"]
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
    res = await apirequest(
        "/warthunder/clan/verify", method="GET", params={"name": name}
    )
    return res
