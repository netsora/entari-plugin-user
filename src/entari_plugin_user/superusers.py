from arclet.entari.config import EntariConfig
from arclet.entari.plugin import keeping
from entari_plugin_database import get_session
from sqlalchemy import select

from .models import Bind, User

_managed_superusers: set[tuple[str, str]] = keeping(
    "managed_superusers", obj_factory=set
)


def preserve_configured_superusers(configured: dict[str, list[str]]) -> None:
    _managed_superusers.difference_update(
        (platform, platform_id)
        for platform, platform_ids in configured.items()
        for platform_id in platform_ids
    )


def apply_entari_superusers(desired: set[tuple[str, str]]) -> None:
    superusers = EntariConfig.instance.basic.superusers

    for platform, platform_id in _managed_superusers - desired:
        platform_users = superusers.get(platform)
        if platform_users is not None:
            platform_users[:] = [
                user_id for user_id in platform_users if user_id != platform_id
            ]
            if not platform_users:
                superusers.pop(platform, None)

    _managed_superusers.intersection_update(desired)

    for binding in desired:
        platform, platform_id = binding
        platform_users = superusers.setdefault(platform, [])
        if platform_id not in platform_users:
            platform_users.append(platform_id)
            _managed_superusers.add(binding)


async def sync_entari_superusers() -> None:
    """将所有权限等级为 5 的账号同步到 Entari 超级用户配置"""
    async with get_session() as db_session:
        binds = (
            await db_session.scalars(
                select(Bind)
                .join(User, User.id == Bind.bind_id)
                .where(User.authority == 5)
            )
        ).all()

    apply_entari_superusers({(bind.platform, bind.platform_id) for bind in binds})
