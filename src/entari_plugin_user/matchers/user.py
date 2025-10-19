from sqlalchemy.exc import IntegrityError
from arclet.alconna import Args, Option, Alconna, CommandMeta
from arclet.entari import command

from ..i18n import Lang
from ..utils import set_user_name
from ..annotated import UserSession


user_alc = Alconna(
    "user",
    Option("-n|--name", Args["name", str], help_text="修改用户名"),
    meta=CommandMeta(
        description="查看用户信息",
        usage=("查看用户信息：/user\n修改用户名：/user -n <用户名>\n"),
        example="/user",
    ),
)
user_alc.shortcut("callme", {"command": "user -n", "fuzzy": True, "prefix": True})
user_disp = command.mount(user_alc)


@user_disp.assign("$main")
async def user_(session: UserSession):
    await session.session.send(
        Lang.user.message(
            platform=session.platform,
            platform_id=session.platform_id,
            user_name=session.user_name,
            created_at=session.created_at.astimezone(),
        )
    )


@user_disp.assign("name")
async def rename_(name: str, session: UserSession):
    try:
        await set_user_name(session.user_id, name)
    except IntegrityError:
        await session.session.send(Lang.user.rename.updated())
    else:
        await session.session.send(Lang.user.rename.duplicate())
