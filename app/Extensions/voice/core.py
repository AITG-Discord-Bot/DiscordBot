from interactions import *
from API.features.voice import voiceApi, dto
from . import state

async def add_jtc_voice_channel(ctx: SlashContext, _):
    try:
        voicechannel = await ctx.guild.create_voice_channel(_("voice_jtc_voice_channel"))
    except Exception as e:
        await ctx.send(_("voice_channel_create_failed"), ephemeral=True)
        return
    voicechannel = voicechannel.id
    guildid = ctx.guild.id
    item = dto.VoiceChannelDTO(serverid=guildid, channelid=voicechannel)
    data = await voiceApi.create_jointocreate(item)
    if guildid not in state.join_to_create_voicechannel.keys():
        state.join_to_create_voicechannel[guildid] = [voicechannel]
    else:
        state.join_to_create_voicechannel[guildid].append(voicechannel)
    voicechannel_url = f"https://discord.com/channels/{guildid}/{voicechannel}"
    await ctx.send(f"voice_jtc_channel_created".format(voicechannel_url), ephemeral=True)