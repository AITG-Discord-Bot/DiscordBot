import logging

from interactions import Client, Member, User, GuildForumPost, BaseChannel

from API import APIRequestError
from API.features.logger import loggerAPI
from API.features.support import supportAPI, request as supporeqdto
from common.core import var
from .. import state


async def init(bot: Client):
    state.support_forum = await bot.fetch_channel(var.support_forum_id)
    support_server = await bot.fetch_guild(var.support_server_id)
    state.devmention = await support_server.fetch_role(var.support_dev_role_id)
    if None in (state.support_forum, state.devmention):
        nonechannel = (
            "support forum channel"
            if state.support_forum is None
            else "developer mention role"
        )
        raise Exception("Failed to initialize on_message_create module.", nonechannel)
    state.devmention = state.devmention.mention
    try:
        await get_logchannels(bot)
    except:
        # No log channels set up yet
        pass


async def teardown():
    dto = []
    for msg in state.messagecache.values():
        dto.append(msg.dto)
    if dto:
        await loggerAPI.add_message_bulk(dto)
    logger = logging.getLogger("AITG")
    logger.info(f"Flushed {len(state.messagecache)} message caches to database.")


async def get_logchannels(bot: Client):
    res = await loggerAPI.get_all()
    for entry in res:
        serverid = entry.serverid
        categoryid = entry.logcategory
        channelid = entry.logchannel
        channel = await bot.fetch_channel(channelid)
        if not channel:
            await loggerAPI.delete_logchannel(serverid, categoryid)
            continue
        if serverid not in state.logchannels.keys():
            state.logchannels[serverid] = {}
        state.logchannels[serverid][categoryid] = channel


def add_logchannel(serverid: int, categoryid: int, channel: BaseChannel):
    if serverid not in state.logchannels.keys():
        state.logchannels[serverid] = {}
    state.logchannels[serverid][categoryid] = channel


async def managecache():
    if len(state.messagecache) < 1500:
        return
    sortedcache = sorted(state.messagecache.items(), key=lambda x: x[1].time)
    old_entries = sortedcache[:500]
    payload = [entry[1].dto for entry in old_entries]
    if payload:
        await loggerAPI.add_message_bulk(payload)
    for key, _ in old_entries:
        state.messagecache.pop(key, None)


async def get_forumchannel(author: Member | User) -> GuildForumPost:
    forumthreadid = None
    if author.id not in state.forumthreads.keys():
        try:
            res = await supportAPI.get(userid=author.id)
            forumthreadid = res.channelid
        except APIRequestError:
            pass
    else:
        forumthreadid = state.forumthreads[author.id]
        forumthread = await state.support_forum.fetch_post(forumthreadid)
        if not forumthread:
            state.forumthreads.pop(author.id)
            try:
                await supportAPI.delete(forumthreadid)
            except APIRequestError:
                pass
            return await get_forumchannel(author)
    if not forumthreadid:
        forumthread = await state.support_forum.create_post(
            name=f"DM_{author.id}",
            content=f"{state.devmention} {author.display_name} : `{author.id}` 님에게서 온 DM 입니다.",
        )
        dto = supporeqdto.ForumChannelReqDTO(userid=author.id, channelid=forumthread.id)
        await supportAPI.create(dto)
        state.forumthreads[author.id] = int(forumthread.id)
    else:
        forumthread = await state.support_forum.fetch_post(forumthreadid)
        if forumthread is None:
            await supportAPI.delete(forumthreadid)
            return await get_forumchannel(author)
        state.forumthreads[author.id] = forumthread.id
    if len(state.forumthreads) > 100:
        state.forumthreads.pop(list(state.forumthreads.keys())[0])
    return forumthread
