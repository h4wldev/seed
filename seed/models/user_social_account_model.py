from sqlalchemy import text, Column, ForeignKey, Integer, String, Text, DateTime, Index

from .mixin import Base, ModelMixin


class UserSocialAccountModel(Base, ModelMixin):
    __tablename__ = 'user_social_accounts'
    __table_args__ = (
        Index('user_id'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    social_id = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    @classmethod
    def q_social_id_and_provider(
        cls,
        social_id: str,
        provider: str
    ) -> 'Query':
        return cls.q()\
            .filter(
                cls.social_id == social_id,
                cls.provider == provider
            )
