import sqlalchemy
import datetime
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    unique_games = sqlalchemy.Column(sqlalchemy.String, default='')
    total_games = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    unique_results = sqlalchemy.Column(sqlalchemy.String, default='')
    answered_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
