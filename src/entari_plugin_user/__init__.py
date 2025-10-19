from arclet.entari import metadata

from .config import Config
from .annotated import User as User
from .annotated import UserSession as UserSession
from .utils import get_user as get_user
from .utils import get_user_by_id as get_user_by_id

metadata(
    name="用户",
    author=[{"name": "KomoriDev", "email": "mute231010@gmail.com"}],
    version="0.1.0",
    description="管理和绑定不同平台的用户",
    readme="README.md",
    config=Config,
)

__all__ = [
    "get_user",
    "get_user_by_id",
    "User",
    "UserSession",
]

from . import matchers as matchers
