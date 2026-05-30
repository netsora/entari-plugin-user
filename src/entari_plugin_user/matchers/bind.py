from expiringdictx import ExpiringDict

from arclet.alconna import Alconna, CommandMeta, Args, Option
from arclet.entari import command, Account, ChannelType

from ..i18n import Lang
from ..annotated import UserSession
from .utils import generate_token, get_bind_list
from ..utils import get_user, set_bind, remove_bind

tokens = ExpiringDict[str, tuple[str, str, int, Account, ChannelType | None]](
    capacity=100, default_age=300
)


bind_alc = Alconna(
    "bind",
    Args["token?", str],
    Option("-l|--list", help_text="绑定列表"),
    Option("-r|--revoke", help_text="解除绑定"),
    meta=CommandMeta(
        description="绑定用户",
        usage=("绑定：/bind\n绑定列表：/bind -l|--list\n解绑：/bind -r|--revoke\n"),
        example="/bind",
    ),
)
bind_disp = command.mount(bind_alc)


@bind_disp.assign("$main")
async def _(token: command.Match[str], session: UserSession):
    if not token.available:
        token.result = generate_token()
        tokens[token.result] = (
            session.platform,
            session.platform_id,
            session.user_id,
            session.internal.account,
            session.channel_type,
        )
        await session.send(Lang.bind.generated_1(token=token.result))
        return

    bind_info = tokens.pop(token.result)
    if bind_info is None:
        await session.send(Lang.bind.expire())
        return

    platform, platform_id, user_id, account, channel_type = bind_info

    if channel_type is not None and channel_type != ChannelType.DIRECT:
        token.result = generate_token()
        tokens[token.result] = (
            session.platform,
            session.platform_id,
            user_id,
            session.internal.account,
            None,
        )
        await session.send(Lang.bind.generated_2(token=token.result))
    elif channel_type is None:
        if session.user_id != user_id:
            await session.send(Lang.bind.same_account())
            return

        platform_user = await account.user_get(platform_id)
        user = await get_user(platform, platform_user)
        await set_bind(session.platform, session.platform_id, user.id)
        await session.send(Lang.bind.success())
    else:
        await set_bind(platform, platform_id, session.user_id)
        await session.send(Lang.bind.success())


@bind_disp.assign("list")
async def _(session: UserSession):
    binds = await get_bind_list(session.platform, session.session.user)

    if not binds:
        await session.send(Lang.bind.no_accounts())
        return

    bind_list = []
    for bind in binds:
        status = "✓" if bind.platform_id == session.platform_id else "✗"
        bind_list.append(f"{status} {bind.platform}: {bind.platform_id}")

    bind_info = "\n".join(bind_list)
    await session.send(Lang.bind.list(list=bind_info))


@bind_disp.assign("revoke")
async def _(session: UserSession):
    result = await remove_bind(session.platform, session.platform_id)
    if result:
        await session.send(Lang.bind.remove_success())
    else:
        await session.send(Lang.bind.remove_original())
