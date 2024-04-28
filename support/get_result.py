from data import db_session
from data.models.result import Result

def get_result(results_count):
    max_result = sorted(results_count.items(), key=lambda x: x[1], reverse=True)[0]
    db_sess = db_session.create_session()
    result = db_sess.query(Result).filter(Result.name == max_result[0]).first()
    result.count_users += 1
    db_sess.commit()
    return result.id, result.name, result.description, result.image_url, result.count_users
