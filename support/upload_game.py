import json
from data import db_session
from data.models.game import Game
from data.models.question import Question
from data.models.answer import Answer
from data.models.result import Result

db_session.global_init("../db/database.sqlite")
db_sess = db_session.create_session()

'''
../static/games/смешарики.json
'''
file_name = input('Введите путь к файлу с тестом: ')
with open(file_name, encoding='utf8') as file:
    data = json.load(file)

    game = Game(name=data["name"], description=data["description"])
    db_sess.add(game)

    for quest in data["questions"]:
        question = Question(text=quest["text"], game_id=game.id, game=game)
        for ans in quest["answers"]:
            answer = Answer(text=ans["text"], add_point=ans["add_point"], question_id=question.id, question=question)

            question.answers.append(answer)
            db_sess.add(answer)
            db_sess.merge(question)

        db_sess.add(question)
        game.questions.append(question)
        db_sess.merge(game)

    for res in data["results"]:
        result = Result(name=res["text"], description=res["description"],
                        image_url=res["image_url"], game_id=game.id, game=game)
        db_sess.add(result)
        game.results.append(result)
        db_sess.merge(game)

    db_sess.commit()

print("Тест успешно загрузился в бд")
