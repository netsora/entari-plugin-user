from datetime import datetime, timezone

from sqlalchemy import func, String, Integer, DateTime

from arclet.entari import Session, MessageEvent, ChannelType
from entari_plugin_database import Base, mapped_column, Mapped


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    """用户 ID"""
    name: Mapped[str] = mapped_column(String(255), unique=True)
    """用户昵称"""
    authority: Mapped[int] = mapped_column(Integer, default=1)
    """权限等级"""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    """创建时间"""


class Bind(Base):
    platform: Mapped[str] = mapped_column(String(32), primary_key=True)
    """平台名"""
    platform_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    """平台账号"""
    bind_id: Mapped[int]
    """用户 ID"""
    original_id: Mapped[int]
    """初始时绑定的用户 ID"""


class UserSession:
    session: Session[MessageEvent]
    user: User

    def __init__(self, session: Session, user: User) -> None:
        self.session = session
        self.user = user

    @property
    def user_id(self) -> int:
        """用户 ID"""
        return self.user.id

    @property
    def platform_id(self) -> str:
        """用户平台账号"""
        return self.session.event.user.id

    @property
    def user_name(self) -> str:
        """用户昵称"""
        return self.user.name

    @property
    def platform(self) -> str:
        """平台名"""
        return self.session.account.platform

    @property
    def channel_type(self) -> ChannelType:
        return self.session.channel.type

    @property
    def created_at(self) -> datetime:
        """用户创建日期"""
        return self.user.created_at.replace(tzinfo=timezone.utc)
