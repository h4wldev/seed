import datetime
import user_agents

from fastapi import Request
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from typing import Optional

from seed.utils.geoip import GeoIP

from . import Base, ModelMixin


class UserLoginHistoryModel(Base, ModelMixin):
    __tablename__ = 'user_login_histories'

    _repr_attrs = ('id', 'user_id', 'success')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    success = Column(Boolean, default=False)
    ip = Column(String, nullable=False)
    location = Column(String)
    provider = Column(String)
    device = Column(String)
    os = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(
        self,
        user_id: int,
        ip: str,
        success: bool = False,
        provider: Optional[str] = None,
        device: Optional[str] = None,
        os: Optional[str] = None
    ) -> None:
        self.user_id = user_id
        self.ip = ip
        self.success = success
        self.provider = provider
        self.device = device
        self.os = os
        self.location = None

        geoip: GeoIP = GeoIP(self.ip)

        if geoip.country and geoip.city:
            self.location = f"{geoip.country['iso_code']}{geoip.city['names']['en']}"

    @classmethod
    def from_request(
        cls,
        user_id: int,
        request: 'Request',
        success: bool = False,
        provider: Optional[str] = None,
    ) -> 'UserLoginHistoryModel':
        assert isinstance(
            request, Request
        ), "request arg must be 'fastapi.Request' type"

        ip: str = request.client.host
        user_agent: 'UserAgent' = user_agents.parse(
            request.headers.get('user-agent', '')
        )

        return cls(
            user_id=user_id,
            ip=ip,
            success=success,
            provider=provider,
            device=user_agent.device.family,
            os=user_agent.os.family,
        )


UserLoginHistory = sqlalchemy_to_pydantic(UserLoginHistoryModel)
