from arclet.entari import MessageChain, ConfigReload, Ready, metadata, plugin
from arclet.entari.event.command import CommandReceive

from .config import Config
from .annotated import User as User
from .annotated import UserSession as UserSession
from .filters import Auth as Auth
from .filters import only_superuser as only_superuser
from .filters import Authorization as Authorization
from .utils import get_user as get_user
from .utils import get_user_by_id as get_user_by_id
from .superusers import preserve_configured_superusers, sync_entari_superusers

metadata(
    name="用户",
    author=[{"name": "KomoriDev", "email": "mute231010@gmail.com"}],
    version="0.1.6",
    description="管理和绑定不同平台的用户",
    readme="README.md",
    config=Config,
)


@plugin.listen(CommandReceive, priority=0)
async def _ignore_blacklisted_commands(user: User):
    if user.authority == 0:
        return MessageChain()


@plugin.listen(Ready)
async def _sync_entari_superusers_on_ready():
    await sync_entari_superusers()


@plugin.listen(ConfigReload)
async def _sync_entari_superusers_on_config_reload(event: ConfigReload):
    if event.scope != "basic" or event.key != "superusers":
        return

    preserve_configured_superusers(event.value)
    await sync_entari_superusers()


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
