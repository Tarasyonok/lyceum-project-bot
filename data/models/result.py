import sqlalchemy
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class Result(SqlAlchemyBase):
    __tablename__ = "result"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    game_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("game.id"))
    game = orm.relationship('Game')

    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    image_url = sqlalchemy.Column(sqlalchemy.String)
    count_users = sqlalchemy.Column(sqlalchemy.Integer, default=0)
