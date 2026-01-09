from datetime import datetime, UTC

from interactions import ChannelType, ThreadChannel, GuildText
from interactions.api.events import MessageUpdate

from API import APIRequestError
from .. import state
from API.features.logger import loggerAPI, request as reqdto


async def handle(event: MessageUpdate):
    bot = event.bot
    before = event.before
    after = event.after
    if not before or not after:
        return
    if after.channel.type == ChannelType.DM:
        return
    if after.author.bot:
        return
    if after.author.id == bot.user.id:
        return
    if before.content == after.content:
        return
    if before.id not in state.messagecache.keys():
        try:
            data = await loggerAPI.get_log_by_messageid(before.id)
        except APIRequestError:
            return
        logchannel = await bot.fetch_channel(int(data.tochannel))
        assert isinstance(logchannel, ThreadChannel | GuildText)
        logmessage = await logchannel.fetch_message(int(data.tomessage))
        if not logmessage:
            return
        # state.messagecache[before.id] = {"msg": logmessage, "time": datetime.now()}
        state.messagecache[before.id] = state.CacheItem(
            msg=logmessage,
            time=datetime.now(UTC),
            dto=reqdto.MessageLogReqDTO(
                fromchannel=data.fromchannel,
                tochannel=data.tochannel,
                tomessage=data.tomessage,
                frommessage=data.frommessage,
            ),
        )
    else:
        logmessage = state.messagecache[before.id].msg
    embed = logmessage.embeds[0]
    field = embed.fields[0]
    field.value = field.value + f"\n\n**Edit**\n{after.content}"
    embed.set_footer(
        text=f"Userid: {after.author.id}\nTimeStamp: {datetime.now(UTC).replace(tzinfo=None).isoformat()}"
    )
    try:
        await logmessage.edit(content="", embeds=embed)
    except:
        pass
