from random import randint
from interactions import GuildText, Role, Guild, Client, Embed
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
    linkrole: Role = None
    available: bool = False
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
        self.serverid = serverid
        self.bot = bot
        self._ = _

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
        if self.linkrole:
            self.linkrole = await self.server.fetch_role(self.linkrole)
        if self.subnews:
            self.subnews = await self.server.fetch_channel(self.subnews)
        if not self._:
            self._ = localizator(self.server.preferred_locale)

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
        clanmaterole = get_mention(self.clanmaterole, self._)
        modrole = get_mention(self.modrole, self._)
        linkrole = get_mention(self.linkrole, self._)
        subnews = get_mention(self.subnews, self._)
        botmessagechannel = get_mention(self.botmessagechannel, self._)
        clanname = get_clanname(self.clanname, self._)

        embed = Embed(
            title="서버 설정",
            description="서버 설정입니다.",
            color=randint(0, 0xFFFFFF),
        )
        embed.add_field(name="비행대원 역할", value=clanmaterole, inline=True)
        embed.add_field(name="관리자 역할", value=modrole, inline=True)
        # embed.add_field(name="계정 연동자 역할", value=linkrole, inline=True)
        embed.add_field(name="봇 메시지 채널", value=botmessagechannel, inline=True)
        embed.add_field(name="썬더 뉴스 채널", value=subnews, inline=True)
        embed.add_field(name="썬더 비행대 이름", value=clanname, inline=True)
        # embed.add_field(name="경고 설정", value=warningactions, inline=False)
        # embed.add_field(name="로그 채널", value=logchannels, inline=False)
        embed.add_field(
            name="환영 메시지",
            value=f">>> {get_str(self.welcomemessage, self._)}",
            inline=False,
        )
        # if deletelogchannelcnt > 0:
        #     embed.set_footer(text=f"삭제된 로그 채널: {deletelogchannelcnt}")
        # else:
        #     embed.set_footer(text="모든 설정이 정상적으로 진행되었습니다!")
        return embed


def get_mention(obj: Role | GuildText | None, _):
    return obj.mention if obj else _("common_not_set")


def get_str(obj: str | None, _):
    return obj if obj else _("common_not_set")


def get_clanname(name, _):
    if name is None:
        return _("common_not_set")
    url = clanbaseurl + quote(name)
    return f"[{name}]({url})"
