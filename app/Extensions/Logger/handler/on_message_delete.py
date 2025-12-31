from datetime import datetime, UTC

from interactions import ChannelType
from interactions.api.events import MessageDelete

from API import APIRequestError
from API.features.logger import loggerAPI
from .. import state


async def handle(event: MessageDelete):
    bot = event.bot
    message = event.message
    if message.channel.type == ChannelType.DM:
        return
    if message.author.id == bot.user.id:
        return
    if message.author.bot:
        return
    if message.id not in state.messagecache.keys():
        try:
            data = await loggerAPI.get_log_by_messageid(message.id)
        except APIRequestError:
            return
        logchannel = await bot.fetch_channel(int(data.tochannel))
        logmessage = await logchannel.fetch_message(int(data.tomessage))
    else:
        logmessage = state.messagecache[message.id].msg
    embed = logmessage.embeds[0]
    embed.title += " Deleted Message"
    embed.set_footer(
        text=f"Userid: {message.author.id}\nTimeStamp: {datetime.now(UTC).replace(tzinfo=None).isoformat()}"
    )
    await logmessage.edit(content="", embeds=embed)
    state.messagecache.pop(message.id)
