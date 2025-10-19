import random
from collections.abc import Sequence

from sqlalchemy import select
from entari_plugin_database import get_session

from ..config import config
from ..utils import get_user
from ..models import Bind


def generate_token() -> str:
    return f"{config.user_token_prefix}{random.randint(100000, 999999)}"


async def get_bind_list(platform: str, platform_id: str) -> Sequence[Bind]:
    async with get_session() as db_session:
        user = await get_user(platform, platform_id)

        binds = (
            await db_session.scalars(select(Bind).where(Bind.bind_id == user.id))
        ).all()

        return binds
