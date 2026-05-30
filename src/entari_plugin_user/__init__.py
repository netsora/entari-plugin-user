from arclet.entari import metadata

from .config import Config
from .annotated import User as User
from .annotated import UserSession as UserSession
from .filters import Auth as Auth
from .filters import only_superuser as only_superuser
from .filters import Authorization as Authorization
from .utils import get_user as get_user
from .utils import get_user_by_id as get_user_by_id

metadata(
    name="用户",
    author=[{"name": "KomoriDev", "email": "mute231010@gmail.com"}],
    version="0.1.6",
    description="管理和绑定不同平台的用户",
    readme="README.md",
    config=Config,
)

__all__ = [
    "get_user",
    "get_user_by_id",
    "User",
    "UserSession",
    "Auth",
    "Authorization",
    "only_superuser",
]

from . import matchers as matchers
