import asyncio
import importlib

from interactions import *
from interactions.api.events import VoiceStateUpdate

from API import APIRequestError
from API.features.voice import voiceApi, dto
from common.guards import is_admin
from common.localization import getname, getdesc, localize
from . import core, tasks, state
from .handler import on_voice_state_update
from common.core import MyFunctions


voicecommands = SlashCommand(name=getname("voice_command_base"))
jtc_voice_channelgroup = voicecommands.group(name=getname("voice_jointocreate"))

class Voice(Extension):
    #===============================================
    # INIT
    # ==============================================
    def __init__(self, bot):
        self.bot = bot
        self.check_voice_channel_availability_task.start()
        asyncio.create_task(self.async_init())

    async def async_init(self):
        state.join_to_create_voicechannel = {}
        state.createdvoicechannels = {}
        try:
            data = await voiceApi.get_jointocreate()
            for row in data:
                serverid = row.serverid
                voicechannel = row.channelid
                if serverid not in state.join_to_create_voicechannel.keys():
                    voicechannel_res = await self.bot.fetch_channel(voicechannel)
                    item = dto.VoiceChannelDTO(serverid=serverid, channelid=voicechannel)
                    if voicechannel_res is None:
                        await voiceApi.delete_jointocreate(item)
                        continue
                    state.join_to_create_voicechannel[serverid] = [voicechannel]
                else:
                    state.join_to_create_voicechannel[serverid].append(voicechannel)
        except APIRequestError as e:
            if e.error_code != 404:
                raise e

        try:
            data = await voiceApi.get_createdvoicechannels()
            for row in data:
                serverid = row.serverid
                voicechannel = row.voicechannel
                if serverid not in state.createdvoicechannels.keys():
                    voicechannel_res = await self.bot.fetch_channel(voicechannel)
                    item = dto.CreatedVoiceChannelDTO(serverid=serverid, voicechannel=voicechannel)
                    if voicechannel_res is None:
                        await voiceApi.delete_createdvoicechannel(item)
                        continue
                    if not voicechannel_res.voice_members:
                        await voiceApi.delete_createdvoicechannel(item)
                        continue
                    state.createdvoicechannels[serverid] = [voicechannel]
                else:
                    state.createdvoicechannels[serverid].append(voicechannel)
        except APIRequestError as e:
            if e.error_code != 404:
                raise e

    #===============================================
    # DROP
    # ==============================================
    def drop(self):
        asyncio.create_task(self.async_drop())
        super().drop()

    async def async_drop(self):
        # save created voice channel
        for serverid, voicechannels in state.createdvoicechannels.items():
            for voicechannel in voicechannels:
                item = dto.CreatedVoiceChannelDTO(serverid=serverid, voicechannel=voicechannel)
                await voiceApi.create_createdvoicechannel(item)

    #===============================================
    # TASKS
    # ==============================================
    @Task.create(IntervalTrigger(hours=1))
    async def check_voice_channel_availability_task(self):
        return await tasks.check_voice_channel_availability(self.bot)


    # ==============================================
    # CONTEXT MENUS
    # ==============================================

    # ==============================================
    # SLASH COMMANDS
    # ==============================================
    @jtc_voice_channelgroup.subcommand(sub_cmd_name=getname("common_add"), sub_cmd_description=getdesc("voice_jtc_add_desc"))
    @check(is_admin)
    @localize()
    async def add_jtc_voice_channel(self, ctx: SlashContext, _):
        return await core.add_jtc_voice_channel(ctx, _)

    # ==============================================
    # LISTENERS
    # ==============================================
    @listen(VoiceStateUpdate, delay_until_ready=True)
    async def on_voice_state_update(self, event: VoiceStateUpdate):
        return await on_voice_state_update.handle(event)


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    importlib.reload(core)
    functions_ = functions
    Voice(bot)


def teardown():
    # functions_.remove()
    pass
