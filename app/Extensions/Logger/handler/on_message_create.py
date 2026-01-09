from random import randint
from typing import Union
from interactions.api.events import MessageCreate
from interactions import *
from common.discordbot import safe_dm
from datetime import datetime
from API.features.logger import request as loggerreqdto
from API.features.support import supportAPI
from API.core import APIRequestError

from .. import state
from .func import get_forumchannel, managecache

emoji = PartialEmoji.from_str(":white_check_mark:")
assert emoji is not None

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
    assert isinstance(message.channel, ThreadChannel | GuildChannel), f"Expected GuildChannel or ThreadChannel, Got {type(message.channel)}"
    guild = message.channel.guild.id
    if isinstance(
        message.channel,
        (GuildForumPost, GuildPublicThread, GuildPrivateThread, GuildNewsThread),
    ):
        channel = message.channel.parent_channel
        if channel == state.support_forum:
            await handle_support(bot, message.channel, message)
            return
        category = message.channel.parent_channel.category
        category = category.id if category else None
    else:
        category = message.channel.category
        category = category.id if category else None
    if guild not in state.logchannels.keys():
        return
    if category not in state.logchannels[guild].keys():
        return
    channel = state.logchannels[guild][category]
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
    dto = loggerreqdto.MessageLogReqDTO(
        frommessage=int(message.id),
        fromchannel=int(message.channel.id),
        tomessage=int(logmessage.id),
        tochannel=int(channel.id),
    )
    state.messagecache[message.id] = state.CacheItem(logmessage, datetime.now(), dto)
    await managecache()


async def handle_support(bot: Client, channel: ThreadChannel, message: Message):
    userid = None
    for user in state.forumthreads.keys():
        if state.forumthreads[user] == channel.id:
            userid = user
    if userid is None:
        try:
            data = await supportAPI.get(channelid=channel.id)
            userid = data.userid
        except APIRequestError:
            return
        state.forumthreads[userid] = channel.id
        if len(state.forumthreads) > 100:
            state.forumthreads.pop(list(state.forumthreads.keys())[0])
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
