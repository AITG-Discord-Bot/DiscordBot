from interactions import ComponentContext
from Extensions.Clanwar.model import ClanwarBase, PARTYACTIONS
from common import RateLimiter


async def on_button(ratelimiter: RateLimiter, ctx: ComponentContext, _):
    author = ctx.author
    message = ctx.message
    custom_id = ctx.custom_id
    author_id = int(author.id)

    if not custom_id.endswith("party"):
        return

    party = ClanwarBase(_, ctx=ctx)

    # 취소 버튼: "<partyid>_cancel_party"
    if custom_id.endswith("_cancel_party"):
        party_id = custom_id.split("_")[0]
        await party.get_party(partyid=party_id)

        if author.id != party.owner.id:
            await ctx.send(_("clanwar_no_owner_area"), ephemeral=True, delete_after=5)
            return

        await ctx.defer()
        await party.cancel_party()
        await ctx.edit_origin(components=[])
        await ctx.send(_("clanwar_canceled"), ephemeral=True, delete_after=5)
        return

    # 레이트 리미트
    if not ratelimiter.get(author_id):
        await ctx.send(
            _("common_ratelimit").format(1, 2),
            ephemeral=True,
            delete_after=5,
        )
        return

    # 파티 정보 로드
    await party.get_party(message=message)

    # 파티장은 여기 버튼 못 씀 (참여/대기/나가기)
    if author.id == party.owner.id:
        await ctx.send(_("clanwar_no_owner_area"), ephemeral=True, delete_after=5)
        return

    # 현재 상태 캐시
    in_participant = author.id in party.participant
    in_primary = author.id in party.primarywaiter
    in_waiter = author.id in party.waiter

    # 1) 나가기
    if custom_id == "exit_party":
        if not (in_participant or in_primary or in_waiter):
            await ctx.send(_("clanwar_not_in_party"), ephemeral=True, delete_after=5)
            return

        await party.remove_people(author)
        await party.edit_embed(save=False)
        await ctx.send(_("clanwar_leave"), ephemeral=True, delete_after=5)
        return

    # 2) 참가 버튼 (join_party)
    if custom_id == "join_party":
        if in_participant:
            # 이미 참가자
            await ctx.send(
                _("clanwar_already_in_party"), ephemeral=True, delete_after=5
            )
            return
        result = await party.add_people(author)
        await party.edit_embed(save=False)
        if result == PARTYACTIONS.PRIMARY_PARTY:
            await ctx.send(_("clanwar_wait_party"), ephemeral=True, delete_after=5)
        else:
            await ctx.send(_("clanwar_join_party"), ephemeral=True, delete_after=5)
        return

    # 3) 대기열 버튼 (wait_party)
    if custom_id == "wait_party":
        if in_waiter:
            await ctx.send(
                _("clanwar_already_in_wait"),
                ephemeral=True,
                delete_after=5,
            )
            return
        await party.add_people(author, wait=True)
        await party.edit_embed(save=False)
        await ctx.send(
            _("clanwar_pending_party"),
            ephemeral=True,
            delete_after=5,
        )
        return
