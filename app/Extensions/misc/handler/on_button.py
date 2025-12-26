from interactions import *
from common import waitforcomponent
from ..utils import decode_embed

anytextchannels = [
    ChannelType.GUILD_TEXT,
    ChannelType.GUILD_NEWS,
    ChannelType.GUILD_NEWS_THREAD,
    ChannelType.GUILD_PUBLIC_THREAD,
    ChannelType.GUILD_PRIVATE_THREAD,
]


async def handle(ctx: ComponentContext, _):
    bot = ctx.bot
    if ctx.custom_id == "submit_embed_url":
        modal = Modal(
            ParagraphText(
                label=_("misc_submit_embed_url_label"),
                custom_id="embed_json",
                placeholder=_("misc_submit_embed_url_label_placeholder"),
                required=True,
            ),
            title=_("misc_submit_embed_url_modal_title"),
        )
        await ctx.send_modal(modal=modal)
        modal_ctx: ModalContext = await bot.wait_for_modal(modal, timeout=300)
        embed_json = modal_ctx.responses["embed_json"]
        embed_json = decode_embed.decode_embed(embed_json)
        embed = Embed.from_dict(embed_json)
        channel_select = ChannelSelectMenu(
            channel_types=anytextchannels,
            placeholder=_("common_select_channel"),
        )
        msg = await modal_ctx.send(
            _("common_select_channel"), components=channel_select, ephemeral=True
        )
        used_ctx = await waitforcomponent(bot, ctx.author, msg, channel_select)
        if used_ctx is None:
            return
        channel: BaseChannel = used_ctx.values[0]
        msg: Message = await channel.send(embeds=embed)
        await used_ctx.send(
            _("misc_submit_embed_url_success").format(msg.jump_url), ephemeral=True
        )
