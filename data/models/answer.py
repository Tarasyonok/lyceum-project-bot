import sqlalchemy
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase):
    __tablename__ = "answer"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("question.id"))
    question = orm.relationship('Question')

    text = sqlalchemy.Column(sqlalchemy.String)
    add_point = sqlalchemy.Column(sqlalchemy.String)
