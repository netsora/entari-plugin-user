from expiringdictx import ExpiringDict
from arclet.alconna import Alconna, CommandMeta, Args, Option
from arclet.entari import command, At

from .utils import generate_token

from ..i18n import Lang
from ..log import logger
from ..annotated import UserSession
from ..filters import authorization
from ..utils import get_user, set_user_authority

tokens = ExpiringDict[str, int](capacity=100, default_age=300)


authorize_alc = Alconna(
    "authorize",
    Args["value?#权限等级", int],
    Option("-u|--user", Args["user#目标用户", At], dest="user_option"),
    Option("--superuser", Args["token?#密钥", str]),
    meta=CommandMeta(
        description="设置用户的权限等级",
        usage="authorize <value> -u <user>",
        example="authorize 3 -u @miraita",
    ),
)
authorize_alc.shortcut("auth", {"command": "authorize", "fuzzy": True, "prefix": True})
authorize_disp = command.mount(authorize_alc)


@authorize_disp.assign("user")
@authorization(4)
async def authorize_(value: int | None, user: At, session: UserSession):
    if value is None or user.id is None:
        return

    operator_user = session.user
    platform_user = await session.user_get(user.id)
    target_user = await get_user(session.platform, platform_user)

    if target_user.authority >= operator_user.authority:
        await session.send(Lang.authority.low_authority())
        return

    if value >= operator_user.authority:
        await session.send(Lang.authority.low_authority())
        return

    await set_user_authority(target_user.id, value)
    await session.send(Lang.authority.success())


@authorize_disp.assign("superuser")
async def auth_superuser_(token: command.Match[str], session: UserSession):
    if not token.available:
        token.result = generate_token("superuser/")
        tokens[token.result] = session.user_id

        logger.opt(colors=True).success(
            "Access granted: <magenta>SUPERUSER</magenta> token created -> "
            + f"<yellow>{token.result}</yellow>"
        )

        resp = await session.session.prompt(
            Lang.authority.superuser_guide(),
            timeout=300,
            priority=20,
        )

        if resp is None:
            return

        bind_info = tokens.pop(resp.extract_plain_text())
    else:
        bind_info = tokens.pop(token.result)

    if bind_info is None:
        await session.send(Lang.bind.expire())
        return

    user_id = bind_info
    await set_user_authority(user_id, 5)
    await session.send(Lang.authority.superuser_authed())
