from interactions import *
from . import state
from API.features.voice import voiceApi, dto

async def check_voice_channel_availability(bot: Client):
    for serverid, voicechannels in state.join_to_create_voicechannel.items():
        for voicechannel in voicechannels:
            voicechannel_res = await bot.fetch_channel(voicechannel)
            if voicechannel_res is None:
                state.join_to_create_voicechannel[serverid].remove(voicechannel)
                if len(state.join_to_create_voicechannel[serverid]) == 0:
                    del state.join_to_create_voicechannel[serverid]
                item = dto.VoiceChannelDTO(serverid=serverid, channelid=voicechannel)
                await voiceApi.delete_jointocreate(item)
    for serverid, voicechannels in state.createdvoicechannels.items():
        for voicechannel in voicechannels:
            voicechannel_res = await bot.fetch_channel(voicechannel)
            if voicechannel_res is None:
                state.createdvoicechannels[serverid].remove(voicechannel)
                if len(state.createdvoicechannels[serverid]) == 0:
                    del state.createdvoicechannels[serverid]
                item = dto.CreatedVoiceChannelDTO(serverid=serverid, voicechannel=voicechannel)
                await voiceApi.delete_createdvoicechannel(item)
