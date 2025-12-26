import logging

from interactions import Client, BaseUser, GuildForumPost, BaseChannel

from . import shared
from common import var, apirequest


async def init(bot: Client):
    shared.support_forum = await bot.fetch_channel(var.support_forum_id)
    support_server = await bot.fetch_guild(var.support_server_id)
    shared.devmention = await support_server.fetch_role(var.support_dev_role_id)
    if None in (shared.support_forum, shared.devmention):
        nonechannel = (
            "support forum channel"
            if shared.support_forum is None
            else "developer mention role"
        )
        raise Exception("Failed to initialize on_message_create module.", nonechannel)
    shared.devmention = shared.devmention.mention
    try:
        await get_logchannels(bot)
    except:
        # No log channels set up yet
        pass


async def teardown():
    json = []
    for msg in shared.messagecache.values():
        json.append(msg["json"])
    if json:
        await apirequest("/logger/messagelog/bulk", json=json)
    logger = logging.getLogger("AITG")
    logger.info(f"Flushed {len(shared.messagecache)} message caches to database.")


async def get_logchannels(bot: Client):
    res: list[dict] = await apirequest("/logger/channels", method="GET")
    for entry in res:
        serverid = entry["serverid"]
        categoryid = entry["logcategory"]
        channelid = entry["logchannel"]
        channel = await bot.fetch_channel(channelid)
        if not channel:
            await apirequest(
                f"/logger/channels/{serverid}/{categoryid}", method="DELETE"
            )
            continue
        if serverid not in shared.logchannels.keys():
            shared.logchannels[serverid] = {}
        shared.logchannels[serverid][categoryid] = channel


def add_logchannel(serverid: int, categoryid: int, channel: BaseChannel):
    if serverid not in shared.logchannels.keys():
        shared.logchannels[serverid] = {}
    shared.logchannels[serverid][categoryid] = channel


async def managecache():
    if len(shared.messagecache) < 1500:
        return
    sortedcache = sorted(shared.messagecache.items(), key=lambda x: x[1]["time"])
    old_entries = sortedcache[:500]
    json_payload = [entry[1]["json"] for entry in old_entries]
    if json_payload:
        await apirequest("logger/messagelog/bulk", json=json_payload)
    for key, _ in old_entries:
        shared.messagecache.pop(key, None)


async def get_forumchannel(author: BaseUser) -> GuildForumPost:
    forumthreadid = None
    if author.id not in shared.forumthreads.keys():
        res = await apirequest(
            "/support/forumchannel",
            params={"userid": author.id},
            method="GET",
            surpress_error=True,
        )
        if res.get("success", False):
            forumthreadid = forumthreadid["data"]["channelid"]
    else:
        forumthreadid = shared.forumthreads[author.id]
        forumthread = await shared.support_forum.fetch_post(forumthreadid)
        if not forumthread:
            shared.forumthreads.pop(author.id)
            await apirequest(
                "/support/forumchannel",
                params={"channelid": forumthreadid},
                method="DELETE",
                surpress_error=True,
            )
            return await get_forumchannel(author)
    if not forumthreadid:
        forumthread = await shared.support_forum.create_post(
            name=f"DM_{author.id}",
            content=f"{shared.devmention} {author.display_name} : `{author.id}` 님에게서 온 DM 입니다.",
        )
        await apirequest(
            "/support/forumchannel",
            json={"userid": author.id, "channelid": forumthread.id},
            method="POST",
        )
        shared.forumthreads[author.id] = int(forumthread.id)
    else:
        forumthread = await shared.support_forum.fetch_post(forumthreadid)
        if forumthread is None:
            await apirequest(
                "/support/forumchannel",
                params={"channelid": forumthreadid},
                method="DELETE",
                surpress_error=True,
            )
            return await get_forumchannel(author)
        shared.forumthreads[author.id] = forumthread.id
    if len(shared.forumthreads) > 100:
        shared.forumthreads.pop(list(shared.forumthreads.keys())[0])
    return forumthread
