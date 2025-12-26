from datetime import datetime, UTC

from interactions import ChannelType
from interactions.api.events import MessageDelete

from common import apirequest
from . import shared


async def handle(event: MessageDelete):
    bot = event.bot
    message = event.message
    if message.channel.type == ChannelType.DM:
        return
    if message.author.id == bot.user.id:
        return
    if message.author.bot:
        return
    if message.id not in shared.messagecache.keys():
        data = await apirequest(
            f"/logger/messagelog/{message.id}", method="GET", surpress_error=True
        )
        if not data.get("sucess", False):
            return
        data = data["data"]
        logchannel = await bot.fetch_channel(int(data["tochannel"]))
        logmessage = await logchannel.fetch_message(int(data["tomessage"]))
    else:
        logmessage = shared.messagecache[message.id]["msg"]
    embed = logmessage.embeds[0]
    embed.title += " Deleted Message"
    embed.set_footer(
        text=f"Userid: {message.author.id}\nTimeStamp: {datetime.now(UTC).replace(tzinfo=None).isoformat()}"
    )
    await logmessage.edit(content="", embeds=embed)
    shared.messagecache.pop(message.id)
