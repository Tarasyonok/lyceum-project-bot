import sqlalchemy
import datetime
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class Game(SqlAlchemyBase):
    __tablename__ = "game"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    played_count = sqlalchemy.Column(sqlalchemy.String)

    questions = orm.relationship('Question', back_populates='game')
    results = orm.relationship('Result', back_populates='game')

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
