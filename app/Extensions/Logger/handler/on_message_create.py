from random import randint
from interactions.api.events import MessageCreate
from interactions import *
from common import apirequest, APIRequestError, safe_dm
from datetime import datetime

from . import shared
from .func import get_forumchannel, managecache

emoji = PartialEmoji.from_str(":white_check_mark:")


async def handle(event: MessageCreate):
    """
    메시지 생성시 이를 감당하는 메인, 여기에서 우선 메시지가 전송된 채널에 따라 각자 함수로 분배
    :param event:
    :return:
    """
    bot = event.bot
    if event.message.author.id == bot.user.id:
        return
    if event.message.author.bot:
        return
    message = event.message
    match message.channel.type:
        case (
            ChannelType.GUILD_TEXT
            | ChannelType.GUILD_NEWS
            | ChannelType.GUILD_PRIVATE_THREAD
            | ChannelType.GUILD_PUBLIC_THREAD
            | ChannelType.GUILD_NEWS_THREAD
        ):
            await log_message(event)
        case ChannelType.DM:
            await bot_dm(event)
        case _:
            pass


async def log_message(event: MessageCreate):
    bot = event.bot
    message = event.message
    guild = message.channel.guild.id
    if isinstance(
        message.channel,
        (GuildForumPost, GuildPublicThread, GuildPrivateThread, GuildNewsThread),
    ):
        channel = message.channel.parent_channel
        if channel == shared.support_forum:
            await handle_support(bot, message.channel, message)
            return
        category = message.channel.parent_channel.category.id
    else:
        category = message.channel.category.id
    if guild not in shared.logchannels.keys():
        return
    if category not in shared.logchannels[guild].keys():
        return
    channel = shared.logchannels[guild][category]
    color = randint(0, 0xFFFFFF)
    embed = Embed(
        title=message.author.display_name, description=message.jump_url, color=color
    )
    if len(message.content) > 0:
        embed.add_field(name="Content", value=">>> " + message.content)
    if len(message.attachments) > 0:
        value = ""
        cnt = 1
        for attachment in message.attachments:
            value += f"{cnt}. {attachment.content_type}: [{attachment.filename}]({attachment.url})\n"
            cnt += 1
        embed.add_field(name="Attachment", value=value)
    embed.set_footer(text=f"Userid: {message.author.id}\nTimeStamp: {datetime.now()}")
    logmessage = await channel.send(content="", embeds=embed)
    json = {
        "frommessage": message.id,
        "fromchannel": message.channel.id,
        "tomessage": logmessage.id,
        "tochannel": channel.id,
    }
    shared.messagecache[message.id] = {
        "msg": logmessage,
        "time": datetime.now(),
        "json": json,
    }
    await managecache()


async def handle_support(bot: Client, channel: GuildForumPost, message: Message):
    userid = None
    for user in shared.forumthreads.keys():
        if shared.forumthreads[user] == channel.id:
            userid = user
    if userid is None:
        try:
            data = await apirequest(
                "/support/forumchannel", params={"channelid": channel.id}
            )
            userid = data["userid"]
        except APIRequestError:
            return
        shared.forumthreads[userid] = channel.id
        if len(shared.forumthreads) > 100:
            shared.forumthreads.pop(list(shared.forumthreads.keys())[0])
    user = await bot.fetch_user(userid)
    if user is None:
        return
    if message.content != "":
        msg = await safe_dm(user, content=message.content)
        if msg is None:  # DM 이 안되는 상황이니 탈출
            return
    if message.attachments:
        for attachment in message.attachments:
            await safe_dm(user, content=attachment.url)
    await message.add_reaction(emoji=emoji)


async def bot_dm(event: MessageCreate):
    message = event.message
    author = message.author
    forumthread = await get_forumchannel(author)
    await forumthread.edit(locked=True)
    if message.content != "":
        await forumthread.send(message.content)
    if message.attachments:
        for attachment in message.attachments:
            await forumthread.send(attachment.url)
    await message.add_reaction(emoji)
