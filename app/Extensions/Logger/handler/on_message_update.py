from datetime import datetime, UTC

from interactions import ChannelType
from interactions.api.events import MessageUpdate
from . import shared
from common import apirequest


async def handle(event: MessageUpdate):
    bot = event.bot
    before = event.before
    after = event.after
    if after.channel.type == ChannelType.DM:
        return
    if after.author.bot:
        return
    if after.author.id == bot.user.id:
        return
    if before.content == after.content:
        return
    if before.id not in shared.messagecache.keys():
        data: dict = await apirequest(
            f"/logger/messagelog/{before.id}", method="GET", surpress_error=True
        )
        if not data.get("success", False):
            return
        data = data["data"]
        logchannel = await bot.fetch_channel(int(data["tochannel"]))
        logmessage = await logchannel.fetch_message(int(data["tomessage"]))
        shared.messagecache[before.id] = {"msg": logmessage, "time": datetime.now()}
    else:
        logmessage = shared.messagecache[before.id]["msg"]
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
