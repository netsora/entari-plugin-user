from arclet.letoderea import Propagator, STOP, enter_if, propagate
from arclet.letoderea.utils import TCallable

from .i18n import Lang
from .annotated import UserSession


class authorization(Propagator):
    def __init__(self, authority: int, priority: int = 90):
        self.success = True
        self.authority = authority
        self.priority = priority

    async def check(self, session: UserSession):
        self.success = session.user.authority >= self.authority
        if not self.success:
            await session.send(Lang.authority.low_authority())
            return STOP

    def compose(self):
        yield self.check, True, self.priority

    def __call__(self, func: TCallable) -> TCallable:
        return propagate(self)(func)


def permission_check(sess: UserSession) -> bool:
    return sess.user.authority == 5


superusers = enter_if(permission_check)
