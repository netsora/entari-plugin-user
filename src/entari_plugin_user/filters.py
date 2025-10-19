from arclet.letoderea import Propagator, STOP

from .i18n import Lang
from .annotated import UserSession


class Authorization(Propagator):
    def __init__(self, authority: int, priority: int = 80):
        self.success = True
        self.authority = authority
        self.priority = priority

    async def before(self, session: UserSession):
        self.success = session.user.authority >= self.authority
        if not self.success:
            await session.session.send(Lang.authority.low_authority())
            return STOP

    async def after(self):
        return

    def compose(self):
        yield self.before, True, self.priority
        yield self.after, False, self.priority
