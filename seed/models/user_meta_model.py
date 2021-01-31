from sqlalchemy import text, Column, ForeignKey, Integer, Boolean, DateTime, Index

from .mixin import Base, ModelMixin


class UserMetaModel(Base, ModelMixin):
    __tablename__ = 'user_meta'
    __table_args__ = (
        Index('user_id'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_promotion = Column(Boolean, default=0)
    email_notification = Column(Boolean, default=0)
    is_certified = Column(Boolean, default=0)
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
