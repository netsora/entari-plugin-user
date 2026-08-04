import asyncio

from sqlalchemy import exc, select
from arclet.entari import User as UserModel
from entari_plugin_database import AsyncSession, get_session

from .models import User, Bind
from .superusers import sync_entari_superusers


_insert_mutex: asyncio.Lock | None = None


def _get_insert_mutex():
    global _insert_mutex

    if _insert_mutex is None:
        _insert_mutex = asyncio.Lock()

    return _insert_mutex


async def _get_user(
    db_session: AsyncSession, platform: str, platform_id: str
) -> User | None:
    return (
        await db_session.scalars(
            select(User)
            .where(Bind.platform_id == platform_id)
            .where(Bind.platform == platform)
            .join(Bind, User.id == Bind.bind_id)
        )
    ).one_or_none()


async def create_user(platform: str, platform_user: UserModel) -> User:
    async with _get_insert_mutex():
        try:
            async with get_session(expire_on_commit=False) as db_session:
                user = User(name=platform_user.name)
                db_session.add(user)
                await db_session.commit()

                bind = Bind(
                    platform=platform,
                    platform_id=platform_user.id,
                    bind_id=user.id,
                    original_id=user.id,
                )
                db_session.add(bind)
                await db_session.commit()

        except exc.IntegrityError:
            async with get_session() as db_session:
                user = await _get_user(
                    db_session,
                    platform,
                    platform_user.id,
                )

                if user is None:
                    raise ValueError("创建用户失败")

    return user


async def get_user(platform: str, platform_user: UserModel) -> User:
    async with get_session() as db_session:
        _user = await _get_user(
            db_session,
            platform,
            platform_user.id,
        )

    if not _user:
        _user = await create_user(platform, platform_user)

    return _user


async def get_user_by_id(user_id: int) -> User:
    async with get_session() as db_session:
        user = (
            await db_session.scalars(select(User).where(User.id == user_id))
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        return user


async def set_user_name(user_id: int, name: str) -> None:
    async with get_session() as db_session:
        user = (
            await db_session.scalars(select(User).where(User.id == user_id))
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        user.name = name
        await db_session.commit()


async def set_user_authority(user_id: int, authority: int) -> None:
    async with get_session() as db_session:
        user = (
            await db_session.scalars(select(User).where(User.id == user_id))
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        user.authority = authority
        await db_session.commit()

    await sync_entari_superusers()


async def set_bind(platform: str, platform_id: str, user_id: int) -> None:
    async with get_session() as db_session:
        bind = (
            await db_session.scalars(
                select(Bind)
                .where(Bind.platform == platform)
                .where(Bind.platform_id == platform_id)
            )
        ).one_or_none()

        if not bind:
            raise ValueError("找不到用户信息")

        bind.bind_id = user_id
        await db_session.commit()

    await sync_entari_superusers()


async def remove_bind(platform: str, platform_id: str) -> bool:
    async with get_session() as db_session:
        bind = (
            await db_session.scalars(
                select(Bind)
                .where(Bind.platform == platform)
                .where(Bind.platform_id == platform_id)
            )
        ).one_or_none()

        if not bind:
            raise ValueError("找不到用户信息")

        if bind.bind_id == bind.original_id:
            return False

        bind.bind_id = bind.original_id
        await db_session.commit()

    await sync_entari_superusers()
    return True
