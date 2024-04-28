import sqlalchemy
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = "question"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    game_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("game.id"))
    game = orm.relationship('Game')

    text = sqlalchemy.Column(sqlalchemy.String)
    answers = orm.relationship('Answer', back_populates='question')
