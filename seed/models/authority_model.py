import datetime

from sqlalchemy import Column, Text, String, DateTime, Index

from . import Base, ModelMixin


class AuthorityModel(Base, ModelMixin):
    __tablename__ = 'authorities'

    _repr_attrs = ('authority')

    authority = Column(String(20), primary_key=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
