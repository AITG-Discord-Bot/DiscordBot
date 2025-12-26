from random import randint
from interactions import (
    GuildText,
    Role,
    Guild,
    Client,
    Embed,
    GuildCategory,
    BaseChannel,
)
from common.localization import localizator
from common import apirequest
from common.var import clanbaseurl
from urllib.parse import quote


class ServerBase:
    serverid: int = None
    server: Guild = None
    modrole: Role = None
    botmessagechannel: GuildText = None
    welcomemessage: str = None
    clanmaterole: Role = None
    clanname: str = None
    subnews: GuildText = None
    newslang: str = None
    # linkrole: Role = None  # 이거 안씀 이제
    available: bool = False
    logchannels: list[dict[GuildCategory, BaseChannel]] = []
    """
    서버 설정 모델
    serverid: 서버 ID
    server: 서버 객체
    modrole: 관리자 역할
    botmessagechannel: 봇 메시지 채널
    welcomemessage: 환영 메시지
    clanmaterole: 비행대원 역할
    clanname: 썬더 비행대 이름
    subnews: 썬더 뉴스 채널
    newslang: 뉴스 언어
    linkrole: 계정 연동자 역할
    available: 서버 사용 가능 여부
    
    Methods:
    get(): 서버 설정을 API에서 가져와서 객체에 설정
    update(**kwargs): 서버 설정을 API에 업데이트
                      update 실행시 굳이 get을 실행하지 않아도 됨
                      근데 이러면 만일 DB에 없는 서버일 경우 에러가 발생합니다.
                      봇이 켜질때 현재 자신이 있는 서버들을 DB에 넣어주기 때문에 이럴 일은 없을거라 생각합니다.
    create_embed(): 서버 설정을 임베드로 생성
    
    """

    def __init__(self, bot: Client, serverid: int, _=None):
        """
        이거 만으로는 아무 의미 없습니다. get()을 실행해야 값이 들어갑니다.
        :param bot:
        :param serverid:
        :param _:
        """
        self.serverid = serverid
        self.bot = bot
        self.localizator = _

    async def get(self):
        res = await apirequest(f"/server/{self.serverid}", "GET")
        for key, value in res.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.server = await self.bot.fetch_guild(self.serverid)
        if self.modrole:
            self.modrole = await self.server.fetch_role(self.modrole)
        if self.botmessagechannel:
            self.botmessagechannel = await self.server.fetch_channel(
                self.botmessagechannel
            )
        if self.clanmaterole:
            self.clanmaterole = await self.server.fetch_role(self.clanmaterole)
        # if self.linkrole:
        #     self.linkrole = await self.server.fetch_role(self.linkrole)
        if self.subnews:
            self.subnews = await self.server.fetch_channel(self.subnews)
        if not self.localizator:
            self.localizator = localizator(self.server.preferred_locale)

    async def update(self, **kwargs):
        json = {}
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                json[key] = value
            else:
                raise AttributeError(f"Unknown attribute: {key}")
        for i in json:
            if isinstance(json[i], Role) or isinstance(json[i], GuildText):
                json[i] = int(json[i].id)
        await apirequest(f"/server/{self.serverid}", "PATCH", json=json)

    async def create_embed(self):
        _ = self.localizator
        await self.get_logchannels()
        clanmaterole = get_mention(self.clanmaterole, self.localizator)
        modrole = get_mention(self.modrole, self.localizator)
        # linkrole = get_mention(self.linkrole, self.localizator)
        subnews = get_mention(self.subnews, self.localizator)
        botmessagechannel = get_mention(self.botmessagechannel, self.localizator)
        clanname = get_clanname(self.clanname, self.localizator)
        logchannels = await self.create_logchannels_str()
        embed = Embed(
            title=_("server_embed_title"),
            description=_("server_embed_desc"),
            color=randint(0, 0xFFFFFF),
        )
        embed.add_field(
            name=_("server_embed_clanmaterole"), value=clanmaterole, inline=True
        )
        embed.add_field(name=_("server_embed_modrole"), value=modrole, inline=True)
        # embed.add_field(name="계정 연동자 역할", value=linkrole, inline=True)
        embed.add_field(
            name=_("server_embed_botmessagechannel"),
            value=botmessagechannel,
            inline=True,
        )
        embed.add_field(name=_("server_embed_newschannel"), value=subnews, inline=True)
        embed.add_field(
            name=_("server_embed_newslang"),
            value=_(f"common_lang_{self.newslang}"),
            inline=True,
        )
        embed.add_field(name=_("server_embed_clanname"), value=clanname, inline=True)
        # embed.add_field(name="경고 설정", value=warningactions, inline=False)
        embed.add_field(
            name=_("server_embed_logchannel"), value=logchannels, inline=False
        )
        embed.add_field(
            name=_("server_embed_welcomemessage"),
            value=f">>> {get_str(self.welcomemessage, self.localizator)}",
            inline=False,
        )
        # if deletelogchannelcnt > 0:
        #     embed.set_footer(text=f"삭제된 로그 채널: {deletelogchannelcnt}")
        # else:
        #     embed.set_footer(text="모든 설정이 정상적으로 진행되었습니다!")
        return embed

    async def get_logchannels(self):
        res: dict = await apirequest(
            f"/logger/channels/{self.serverid}", "GET", surpress_error=True
        )
        if not res.get("success", False):
            return
        for item in res["data"]:
            categoryid = int(item["logcategory"])
            channelid = int(item["logchannel"])
            category = await self.bot.fetch_channel(categoryid)
            channel = await self.server.fetch_channel(channelid)
            if category and channel:
                self.logchannels.append({category: channel})
            else:
                await apirequest(
                    f"/logger/channels/{self.serverid}/{categoryid}",
                    method="DELETE",
                    surpress_error=True,
                )

    async def create_logchannels_str(self):
        if not self.logchannels:
            return ">>> " + self.localizator("common_not_set")
        logchannels = ""
        for item in self.logchannels:
            for category, channel in item.items():
                logchannels += f"📁{category.name} → {channel.mention}\n"
        return logchannels


def get_mention(obj: Role | GuildText | None, _):
    return obj.mention if obj else _("common_not_set")


def get_str(obj: str | None, _):
    return obj if obj else _("common_not_set")


def get_clanname(name, _):
    if name is None:
        return _("common_not_set")
    url = clanbaseurl + quote(name)
    return f"[{name}]({url})"
