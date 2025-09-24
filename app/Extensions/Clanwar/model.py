import asyncio
import copy
from random import randint
from typing import Union
from common.localization import localizator, default_locale

from interactions import (
    Client,
    SlashContext,
    GuildText,
    StringSelectMenu,
    StringSelectOption,
    Member,
    Role,
    AllowedMentions,
    ActionRow,
    ButtonStyle,
    Button,
    Embed,
    Message,
    ComponentContext,
)
from datetime import datetime
import time
from json import loads

from common import apirequest


def addthread(_):
    return StringSelectOption(label=_("clanwar.add_thread"), value="add_thread")


def delthread(_):
    return StringSelectOption(label=_("clanwar.del_thread"), value="delete_thread")


def setvoicechannel(_):
    return StringSelectOption(
        label=_("clanwar.set_voicechannel"), value="edit_voicechannel"
    )


def startparty(_):
    return StringSelectOption(label=_("clanwar.start"), value="start")


def changeowner(_):
    return StringSelectOption(label=_("clanwar.change_owner"), value="change_owner")


def partyowneractions(_):
    return [
        StringSelectOption(label=_("clanwar.end"), value="end"),
        StringSelectOption(label=_("clanwar.delete"), value="delete"),
    ]


class ClanwarBase:
    """
    creates new party
    partyid is automatically generated
    to get existing party, use get_party(partyid or messageid)
    """

    def __init__(
        self,
        _=None,
        bot: Client = None,
        ctx: Union[SlashContext, ComponentContext] = None,
    ):
        """
        initialize party class
        :param _: localization function
        :param bot: interactions bot
        :param ctx: interactions context
        """
        self._ = _
        self.bot = bot
        self.ctx = ctx
        if bot is None and ctx is not None:
            self.bot = ctx.bot
        self.partyid = None
        self.server = None
        self.channel = None
        self.owner = None
        if ctx is not None:
            self.server = ctx.guild
            self.channel: GuildText = ctx.channel
            self.owner = ctx.author
        self.message: Message = None
        self.name = None
        self.desc = None
        self.game = None
        self.time = None
        self.threadid: int = None
        self.thread = None
        self.participant = []
        self.primarywaiter = []
        self.waiter = []
        self.voicechannelid: int = None
        self.voicechannel = None

    async def create_party(self, ctx: SlashContext, desc, game, time, role: Role):
        self.bot = ctx.bot
        self.ctx = ctx
        self.server = ctx.guild
        self.channel = ctx.channel
        self.owner = ctx.author
        self.desc = desc
        self.game = game
        # self.name = f"클랜전 모집, BR: {self.game}"
        self.time = time
        await self.send_message(save=False, role=role)
        json = {
            "serverid": self.server.id,
            "time": self.time,
            "ownerid": self.owner.id,
            "battlerating": self.game,
            "channelid": self.channel.id,
            "messageid": self.message.id,
            "description": self.desc,
        }
        clanwarinfo = await apirequest("/clanwar/", json=json, method="POST")
        self.partyid = clanwarinfo["idx"]
        await self.edit_message()

    async def get_party(
        self, ctx=None, partyid=None, message: Message = None, messageid=None
    ):
        """
        get party from partyid
        bot: interactions bot
        partyid: partyid to get
        """
        if ctx is not None:
            self.ctx = ctx
            self.bot = ctx.bot
        if message is not None:
            messageid = int(message.id)
            self.message = message
            self.channel = message.channel
            self.server = self.channel.guild
        if partyid is not None:
            partyinfo = await apirequest(f"/clanwar/{partyid}", method="GET")
        elif messageid is not None:
            partyinfo = await apirequest(f"/clanwar/message/{messageid}", method="GET")
        else:
            return
        info = partyinfo
        people = info["people"]
        self.partyid = info["idx"]
        self.server = await self.bot.fetch_guild(info["serverid"])
        locale = self.server.preferred_locale or default_locale
        self._ = localizator(locale)
        self.channel = await self.bot.fetch_channel(info["channelid"])
        self.message = await self.channel.fetch_message(info["messageid"])
        self.desc = info["description"]
        self.game = info["battlerating"]
        # self.name = f"클랜전 모집, BR: {self.game}"
        self.time = datetime.fromisoformat(info["time"]).strftime("%Y-%m-%d %H:%M")
        self.owner = await self.server.fetch_member(info["ownerid"])
        if info["threadid"] is not None:
            self.threadid = info["threadid"]
            self.thread = await self.server.fetch_thread(info["threadid"])
        if info["voicechannelid"] is not None:
            self.voicechannelid = info["voicechannelid"]
            self.voicechannel = await self.bot.fetch_channel(info["voicechannelid"])
        temp_participant = {}
        temp_primarywaiter = {}
        temp_waiter = {}
        for person in people:
            if int(person["usertype"]) == 0:
                temp_participant[person["idx"]] = person["userid"]
            elif int(person["usertype"]) == 1:
                temp_primarywaiter[person["idx"]] = person["userid"]
            elif int(person["usertype"]) == 2:
                temp_waiter[person["idx"]] = person["userid"]
        self.participant = [temp_participant[key] for key in sorted(temp_participant)]
        self.primarywaiter = [
            temp_primarywaiter[key] for key in sorted(temp_primarywaiter)
        ]
        self.waiter = [temp_waiter[key] for key in sorted(temp_waiter)]

    def set_voicechannel(self, voicechannel):
        self.voicechannel = voicechannel
        self.voicechannelid = voicechannel.id
        asyncio.create_task(self.log_action(self.owner, PARTYACTIONS.EDIT_VOICECHANNEL))

    async def change_owner(self, owner: Member):
        await self.remove_people(self.owner)
        await self.remove_people(owner)
        self.owner = owner
        await self.edit_message(save=True)

    async def add_thread(self):
        if self.thread is not None:
            return False
        thread = await self.channel.create_thread_from_message(
            name=self._("clanwar.party_author").format(self.owner.display_name),
            message=self.message,
            auto_archive_duration=10080,
        )
        self.thread = thread
        self.threadid = thread.id
        await self.edit_message(save=True)
        await self.log_action(self.owner, PARTYACTIONS.ADD_THREAD)
        # add party members to thread
        for user in self.participant + self.primarywaiter + self.waiter:
            member = await self.server.fetch_member(user)
            await thread.add_member(member)
        return True

    async def del_thread(self):
        if self.thread is None:
            return False
        await self.thread.delete()
        self.thread = None
        self.threadid = None
        await self.edit_message(save=True)
        # await self.log_action(self.owner, PARTYACTIONS.DELETE_THREAD)
        return True

    async def log_action(self, user: Member, action):
        if self.thread is not None:
            await self.thread.send(
                self._("clanwar.logmessage").format(
                    user.mention, self._(f"clanwar.partyaction.{action}")
                )
            )

    async def send_message(self, save=True, role: Role = None):
        embed = await self.create_embed()
        components = await self.create_components()
        msg = ""
        if role is not None:
            msg = role.mention
        message = await self.ctx.send(
            content=msg,
            embed=embed,
            components=components,
            allowed_mentions=AllowedMentions.all(),
        )
        self.message = message
        if save:
            await self.save_partyinfo()

    async def edit_message(self, save=False):
        embed = await self.create_embed()
        components = await self.create_components()
        await self.message.edit(
            embed=embed, components=components, allowed_mentions=AllowedMentions.all()
        )
        if save:
            await self.save_partyinfo()

    async def edit_embed(self, save=True):
        embed = await self.create_embed()
        await self.message.edit(embed=embed)
        if save:
            await self.save_partyinfo()

    async def edit_component(self, save=True):
        components = await self.create_components()
        await self.message.edit(components=components)
        if save:
            await self.save_partyinfo()

    async def create_components(
        self, started=False, disable_select=False, disable_button=False
    ):
        row1 = ActionRow()
        select = copy.deepcopy(partyowneractions(self._))
        if not started:
            select.append(startparty(self._))
            select.append(setvoicechannel(self._))
            if self.thread is None:
                select.append(addthread(self._))
            else:
                select.append(delthread(self._))
            select.append(changeowner(self._))
        row1.add_component(
            StringSelectMenu(
                *select,
                custom_id="manage_party",
                placeholder=self._("clanwar.only_owner_area"),
                min_values=1,
                max_values=1,
                disabled=disable_select,
            )
        )
        row2 = ActionRow(
            Button(
                label=self._("clanwar.join"),
                custom_id="join_party",
                style=ButtonStyle.GREEN,
                disabled=disable_button,
            ),
            Button(
                label=self._("clanwar.wait"),
                custom_id="wait_party",
                style=ButtonStyle.BLUE,
                disabled=disable_button,
            ),
            Button(
                label=self._("clanwar.exit"),
                custom_id="exit_party",
                style=ButtonStyle.RED,
                disabled=disable_button,
            ),
        )
        return [row1, row2]

    async def create_embed(self, started=False, ended=False, auto_end=False):
        self.name = self._("clanwar.party_name").format(self.game)
        embed = Embed(
            title=self.name, description=self.desc, color=randint(0, 0xFFFFFF)
        )
        embed.set_author(
            name=self._("clanwar.party_author").format(self.owner.display_name),
            icon_url=self.owner.avatar_url,
        )
        # print(self.participant)
        if started:
            partytime = datetime.now()
            partytime = int(time.mktime(partytime.timetuple()))
            partytime = f"<t:{partytime}:R>"
            embed.add_field(
                name=self._("clanwar.started"),
                value=self._("clanwar.started_time").format(partytime),
                inline=False,
            )
        elif ended:
            partytime = datetime.now()
            partytime = int(time.mktime(partytime.timetuple()))
            partytime = f"<t:{partytime}:F>"
            auto = ""
            if auto_end:
                auto = self._("clanwar.auto_end")
            embed.add_field(
                name=self._("clanwar.ended"),
                value=self._("clanwar.ended_time").format(partytime, auto),
                inline=False,
            )
        else:
            embed.add_field(
                name=self._("common.time"), value=maketimestr(self.time), inline=True
            )
        participant_str = f"> <@{self.owner.id}> "
        for user in self.participant:
            participant_str += f"<@{user}> "
        embed.add_field(
            name=self._("clanwar.participant_count").format(len(self.participant) + 1),
            value=participant_str,
            inline=False,
        )
        if len(self.primarywaiter) > 0:
            primarywaiter_str = "> "
            for user in self.primarywaiter:
                primarywaiter_str += f"<@{user}> "
            embed.add_field(
                name=self._("clanwar.primary_waiters"),
                value=primarywaiter_str,
                inline=False,
            )
        else:
            embed.add_field(
                name=self._("clanwar.primary_waiters"),
                value="> " + self._("clanwar.no_primary_waiters"),
                inline=False,
            )
        if len(self.waiter) > 0:
            waiter_str = "> "
            for user in self.waiter:
                waiter_str += f"<@{user}> "
            embed.add_field(
                name=self._("clanwar.waiters"), value=waiter_str, inline=False
            )
        else:
            embed.add_field(
                name=self._("clanwar.waiters"),
                value="> " + self._("clanwar.no_waiters"),
                inline=False,
            )
        footer = self._("clanwar.party_id").format(self.partyid)
        if self.voicechannel is None:
            footer += "\n" + self._("clanwar.no_voicechannel")
        else:
            embed.url = (
                f"https://discord.com/channels/{self.server.id}/{self.voicechannel.id}"
            )
        embed.set_footer(text=footer)
        return embed

    async def save_partyinfo(self):
        # if party already exists, update
        json = {
            "serverid": self.server.id,
            "time": self.time,
            "ownerid": self.owner.id,
            "battlerating": self.game,
            "channelid": self.channel.id,
            "messageid": self.message.id,
            "description": self.desc,
            "threadid": self.threadid,
            "voicechannelid": self.voicechannelid,
        }
        await apirequest(f"/clanwar/{self.partyid}", json=json, method="PATCH")

    async def add_people(self, user: Member, wait=False):
        returnval = None
        if wait:  # add user to waiter
            self.waiter.append(user.id)
            await apirequest(
                f"/clanwar/people/{self.partyid}",
                json={
                    "userid": user.id,
                    "usertype": PARTYACTIONS.WAIT_PARTY,
                },
                method="POST",
            )
            await self.log_action(user, PARTYACTIONS.WAIT_PARTY)
            returnval = PARTYACTIONS.WAIT_PARTY
        else:
            # from here, seperate paticipant and primarywaiter
            if len(self.participant) >= 7:
                # add to primarywaiter
                self.primarywaiter.append(user.id)
                await apirequest(
                    f"/clanwar/people/{self.partyid}",
                    json={
                        "userid": user.id,
                        "usertype": PARTYACTIONS.PRIMARY_PARTY,
                    },
                    method="POST",
                )
                await self.log_action(user, PARTYACTIONS.PRIMARY_PARTY)
                returnval = PARTYACTIONS.PRIMARY_PARTY
            else:
                self.participant.append(user.id)
                await apirequest(
                    f"/clanwar/people/{self.partyid}",
                    json={
                        "userid": user.id,
                        "usertype": PARTYACTIONS.JOIN_PARTY,
                    },
                    method="POST",
                )
                await self.log_action(user, PARTYACTIONS.JOIN_PARTY)
                returnval = PARTYACTIONS.JOIN_PARTY
        if self.thread is not None:
            threadmembers = await self.get_thread_member()
            if (user not in threadmembers) and (user.id != self.owner.id):
                await self.thread.add_member(user)
        return returnval

    async def remove_people(self, user: Member):
        wasparticipant = False
        if user.id in self.participant:
            self.participant.remove(user.id)
            wasparticipant = True
        elif user.id in self.primarywaiter:
            self.primarywaiter.remove(user.id)
        elif user.id in self.waiter:
            self.waiter.remove(user.id)
        else:
            return
        await apirequest(f"/clanwar/people/{self.partyid}/{user.id}", method="DELETE")
        if wasparticipant and len(self.primarywaiter) > 0:
            # move primarywaiter to participant
            mover = self.primarywaiter.pop(0)
            await apirequest(f"/clanwar/people/{self.partyid}/{mover}", method="DELETE")
            self.participant.append(mover)
            await apirequest(
                f"/clanwar/people/{self.partyid}",
                json={
                    "userid": mover,
                    "usertype": PARTYACTIONS.JOIN_PARTY,
                },
                method="POST",
            )
        await self.log_action(user, PARTYACTIONS.EXIT_PARTY)
        if self.thread is not None:
            try:
                threadmembers = await self.get_thread_member()
                if (user in threadmembers) and (user.id != self.owner.id):
                    await self.thread.remove_member(user)
            except Exception:  # TODO: 이건 뭐지
                pass
        return

    async def get_thread_member(self):
        if self.thread is not None:
            threadmembers = await self.thread.fetch_members()
            for i, member in enumerate(threadmembers):
                threadmembers[i] = await member.fetch_user()
            return threadmembers
        return []

    async def notify(self):
        for person in self.participant + self.primarywaiter + self.waiter:
            try:
                user = await self.server.fetch_member(person[0])
                dmchannel = await user.fetch_dm()
                await dmchannel.send(
                    self._("clanwar.notification_message").format(
                        self.server.name, self.owner.display_name, self.message.jump_url
                    )
                )
            except Exception:
                pass
        # send party owner too
        ownerdmchannel = await self.owner.fetch_dm()
        await ownerdmchannel.send(
            self._("clanwar.owner_notification_message").format(
                self.server.name, self.message.jump_url
            )
        )
        await self.set_notified()

    async def set_notified(self):
        await apirequest(f"/clanwar/{self.partyid}/notified", method="POST")
        return

    async def start_party(self):
        components = await self.create_components(started=True, disable_button=True)
        embed = await self.create_embed(started=True)
        await self.message.edit(embed=embed, components=components)
        await self.log_action(self.owner, PARTYACTIONS.START_PARTY)
        return

    async def end_party(self, auto=False):
        if self.message is None:
            self.bot.logger.info(f"{self.partyid} has a None Message")
            return
        components = await self.create_components(
            started=True, disable_select=True, disable_button=True
        )
        embed = await self.create_embed(ended=True, auto_end=auto)
        await self.message.edit(embed=embed, components=components)
        await self.log_action(self.owner, PARTYACTIONS.END_PARTY)
        await self.delete(del_message=False)

    async def delete(self, del_message=True):
        """Delete party from db as well as party's message and threadchannel"""
        await apirequest(f"/clanwar/{self.partyid}", method="DELETE")
        if self.thread is not None:
            if del_message:
                await self.thread.delete()
            else:
                await self.thread.archive(locked=True, reason=self._("clanwar.ended"))
        if del_message:
            try:
                await self.message.delete()
            except Exception:
                pass


class PARTYACTIONS:
    JOIN_PARTY = 0
    PRIMARY_PARTY = 1
    WAIT_PARTY = 2
    EXIT_PARTY = 3
    ADD_THREAD = 10
    DELETE_THREAD = 11
    EDIT_VOICECHANNEL = 12
    START_PARTY = 20
    END_PARTY = 21


def maketimestr(timestr):
    partytime = datetime.strptime(timestr, "%Y-%m-%d %H:%M")
    partytime = int(time.mktime(partytime.timetuple()))
    partytime = f"<t:{partytime}:F>\n(<t:{partytime}:R>)"
    return partytime
