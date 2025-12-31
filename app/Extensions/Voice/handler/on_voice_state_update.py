from interactions import Permissions
from interactions.api.events import VoiceStateUpdate

from common.localization import localizator
from ..state import createdvoicechannels, join_to_create_voicechannel

async def handle(event: VoiceStateUpdate):
    guild = None
    _ = None
    before, after = event.before, event.after
    beforemember, aftermember = None, None
    beforechannel, afterchannel = None, None
    beforechannelmember, afterchannelmember = None, None
    if before is not None:
        guild = before.guild
        _ = localizator(guild.preferred_locale)
        beforemember = before.member
        beforechannel = before.channel
        beforechannelmember = beforechannel.voice_members
    if after is not None:
        guild = after.guild
        _ = localizator(guild.preferred_locale)
        aftermember = after.member
        afterchannel = after.channel
        afterchannelmember = afterchannel.voice_members
    if beforemember is None and aftermember is None:
        return
    if beforemember is not None and beforemember.bot:
        return
    if aftermember is not None and aftermember.bot:
        return
    if beforechannel is None and afterchannel is None:
        return
    if beforechannel is not None and afterchannel is not None:
        if beforechannel.id == afterchannel.id:
            return
    if guild.id not in join_to_create_voicechannel.keys() and guild.id not in createdvoicechannels.keys():
        return
    if afterchannel is not None:
        if guild.id in join_to_create_voicechannel.keys():
            if afterchannel.id in join_to_create_voicechannel[guild.id]:
                # create voice channel
                category = afterchannel.category
                if category is None:
                    return
                channel = await category.create_voice_channel(f"{aftermember.display_name}'s channel")
                await channel.add_permission(aftermember, allow=Permissions.MANAGE_CHANNELS)
                await aftermember.move(channel.id)
                if guild.id in createdvoicechannels.keys():
                    createdvoicechannels[guild.id].append(channel.id)
                else:
                    createdvoicechannels[guild.id] = [channel.id]

    if beforechannel is not None:
        if guild.id in createdvoicechannels.keys():
            if beforechannel.id in createdvoicechannels[guild.id]:
                # delete voice channel
                if len(beforechannelmember) == 1:
                    await beforechannel.delete()
                    createdvoicechannels[guild.id].remove(beforechannel.id)
                    if len(createdvoicechannels[guild.id]) == 0:
                        del createdvoicechannels[guild.id]