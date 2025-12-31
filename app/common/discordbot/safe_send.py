from typing import Optional, Tuple
from interactions import *


def _missing_perms(perms: Permissions, need: set[Permissions]) -> set[Permissions]:
    # IntFlag 비트 마스크 체크: 필요한 비트가 모두 켜져 있어야 충족
    return {p for p in need if (perms & p) != p}


async def safe_send(
    bot: Client,
    channel: GuildText,
    content: Optional[str] = None,
    embeds: Optional[list[Embed]] = None,
    components: Optional[list[BaseComponent]] = None,
    attachments: Optional[list[Attachment]] = None,
) -> Message | None:
    # 1) 필요한 권한 도출
    if not channel:
        return None
    need: set[Permissions] = {Permissions.VIEW_CHANNEL, Permissions.SEND_MESSAGES}
    if embeds:
        need.add(Permissions.EMBED_LINKS)
    if attachments:
        need.add(Permissions.ATTACH_FILES)

    # 2) 길드 내 봇 멤버 조회
    guild = channel.guild
    me_id = bot.user.id
    me: Optional[Member] = guild.get_member(me_id)
    if me is None:
        try:
            me = await guild.fetch_member(me_id)
        except Exception:
            return None  # 멤버 확인 실패 시 보수적으로 실패

    # 3) 채널 권한 계산(비트마스크)
    try:
        perms: Permissions = channel.permissions_for(me)
    except Exception:
        return None

    missing = _missing_perms(perms, need)
    if missing:
        return None

    # 4) 전송
    kwargs = {}
    if embeds:
        kwargs["embeds"] = embeds
    if components:
        kwargs["components"] = components
    if attachments:
        kwargs["attachments"] = attachments

    try:
        message = await channel.send(content=content, **kwargs)
        return message
    except Exception:
        # 런타임 오류 시 부족권한은 빈 집합으로 반환(원인 파악은 호출부 로깅 권장)
        return None


async def safe_dm(
    user: Member | User,
    content: Optional[str] = None,
    embeds: Optional[list[Embed]] = None,
    components: Optional[list[BaseComponent]] = None,
    attachments: Optional[list[Attachment]] = None,
) -> Message | None:
    """
    사용자가 DM 차단했거나, 전송 실패 시 None 반환.
    """
    if user is None:
        return None
    try:
        # 1) DM 채널 확보
        dm_channel = await user.fetch_dm()

        # 2) 전송 인자 구성
        kwargs = {}
        if embeds:
            kwargs["embeds"] = embeds
        if components:
            kwargs["components"] = components
        if attachments:
            kwargs["attachments"] = attachments

        # 3) 전송 시도
        message = await dm_channel.send(content=content, **kwargs)
        return message

    except Exception:
        # 유저가 DM 차단하거나 메시지 수신 불가한 경우 등
        return None
