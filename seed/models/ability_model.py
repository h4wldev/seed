import datetime

from sqlalchemy import Column, Text, String, DateTime

from .mixin import Base, ModelMixin


class AbilityModel(Base, ModelMixin):
    __tablename__ = 'abilities'

    _repr_attrs = ('ability',)

    ability = Column(String(20), primary_key=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
