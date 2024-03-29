from typing import List
from askmate import db
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from askmate.models import Users, Tag, Question, QuestionTag, Answer, UserVotes, CommentForQuestion, CommentForAnswer


def switch_asc_desc(order_direction: str) -> str:
    if order_direction == 'asc':
        return 'desc'
    else:
        return 'asc'


def commit_to_database(data) -> None:
    try:
        db.session.add(data)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def update_to_database() -> None:
    db.session.commit()


def register_new_user(new_user: dict) -> None:
    user = Users(user_name=new_user.get('user_name'), email=new_user.get('email'), password=new_user.get('password'), picture=new_user.get('picture'))
    commit_to_database(user)


def ask_new_question(new_question: dict) -> None:
    question = Question(user_id=new_question.get('user_id'), title=new_question.get('title'), message=new_question.get('message'), image=new_question.get('image'), tag_id=new_question.get('tag_id'))
    commit_to_database(question)


def add_new_answer(new_answer: dict) -> None:
    answer = Answer(user_id=new_answer.get('user_id'), message=new_answer.get('message'), question_id=new_answer.get('question_id'))
    commit_to_database(answer)


def add_new_comment_for_question(new_comment: dict) -> None:
    comment = CommentForQuestion(user_id=new_comment.get('user_id'), question_id=new_comment.get('question_id'), message=new_comment.get('message'))
    commit_to_database(comment)


def add_new_comment_for_answer(new_comment: dict) -> None:
    comment = CommentForAnswer(question_id=new_comment.get('question_id'), user_id=new_comment.get('user_id'), answer_id=new_comment.get('answer_id'), message=new_comment.get('message'))
    commit_to_database(comment)


def vote_for_answer(data_to_modify: dict, user_id: str) -> None:
    answer_id = int(data_to_modify.get('answer_id'))
    vote_value = int(data_to_modify.get('answers_votes'))
    db.session.query(Answer).filter(Answer.answer_id == answer_id).update({Answer.vote_number: Answer.vote_number + vote_value})
    update_to_database()
    vote = UserVotes(user_id=int(user_id), answer_id=answer_id, has_voted=vote_value)
    commit_to_database(vote)


def modify_user_reputation(data_to_modify: dict) -> None:
    vote_value = 0
    user = find_user_by_id(user_id=data_to_modify.get('user_id'))
    if 'questions_votes' in data_to_modify:
        vote_value = int(data_to_modify.get('questions_votes'))
    elif 'answers_votes' in data_to_modify:
        vote_value = int(data_to_modify.get('answers_votes'))
    if vote_value > 0:
        user.reputation += 5
    else:
        user.reputation -= 5
    update_to_database()


def vote_for_question_user_votes_table(question_id: int, user_id: int, vote_value: int) -> None:
    vote = UserVotes(user_id=user_id, question_id=question_id, has_voted=vote_value)
    commit_to_database(vote)


def check_user_question_vote(user_id: int, question_id: int) -> None:
    return UserVotes.query.filter_by(user_id=user_id, question_id=question_id)


def check_user_answer_vote(user_id: int, answer_id: int) -> None:
    return db.session.query(UserVotes).filter_by(user_id=user_id, answer_id=answer_id)


def update_answer(updated_answer: dict) -> None:
    question_id = updated_answer.get('question_id')
    message = updated_answer.get('message')
    db.session.query(Answer).filter(Answer.question_id == question_id).update({Answer.message: message})
    update_to_database()


def find_user_by_email(email: str) -> Users:
    return Users.query.filter_by(email=email).first()


def fetch_tags() -> Tag:
    return Tag.query.all()


def fetch_users(request_args: dict) -> List[Users]:
    page = int(request_args.get('page', int(1)))
    order_by = request_args.get('order_by', 'user_name')
    order_direction = request_args.get('order_direction', 'asc')
    users = "Users.query.order_by(Users.{}.{}())".format(order_by, order_direction)
    return eval(users).paginate(page, per_page=21)


def func_count_tags():
    return db.engine.execute('SELECT tag.tag_id, tag.tag_name, count(question.tag_id) as count FROM tag, question WHERE question.tag_id = tag.tag_id GROUP BY tag.tag_name, tag.tag_id;')


def choice_query() -> Tag:
    return Tag.query


def find_question_by_id(question_id: int) -> Question:
    return Question.query.get_or_404(question_id)


def remove_question_by_id(question_id: int) -> None:
    Question.query.filter_by(question_id=question_id).delete()
    update_to_database()


def remove_comment_for_question_by_id(comment_id: int) -> None:
    CommentForQuestion.query.filter_by(comment_id=comment_id).delete()
    update_to_database()


def remove_comment_for_answer_by_id(comment_id):
    CommentForAnswer.query.filter_by(comment_id=comment_id).delete()
    update_to_database()


def remove_answer_by_id(answer_id: int) -> None:
    Answer.query.filter_by(answer_id=answer_id).delete()
    update_to_database()


def func_find_last_10_question_titles() -> Question:
    return Question.query.with_entities(Question.question_id, Question.title, Question.vote_number).order_by(Question.submission_time.desc()).limit(10).all()


def func_find_top_10_users() -> Users:
    return Users.query.with_entities(Users.user_id, Users.user_name, Users.reputation).order_by(Users.reputation.desc()).limit(10).all()


def find_answers_by_question_id(question_id: int) -> Answer:
    return Answer.query.filter_by(question_id=question_id).order_by(Answer.submission_time.asc())


def find_comments_by_question_id(question_id: int) -> CommentForQuestion:
    return CommentForQuestion.query.filter_by(question_id=question_id).order_by(CommentForQuestion.submission_time.asc())


def find_comments_by_answer_id(answer_id: int) -> CommentForAnswer:
    return CommentForAnswer.query.filter_by(answer_id=answer_id).order_by(CommentForAnswer.submission_time.asc())


def find_tag_name_by_id(tag_id: int) -> Tag:
    return Tag.query.filter_by(tag_id=tag_id).first()


def find_question_tag_by_id(question_id: int) -> QuestionTag:
    return QuestionTag.query.filter_by(question_id=question_id).first()


def count_answers_by_question_id(question_id: int) -> Answer:
    return Answer.query.filter_by(question_id=question_id).count()


def count_comments_by_question_id(question_id: int) -> CommentForQuestion:
    return CommentForQuestion.query.filter_by(question_id=question_id).count()


def find_user_by_id(user_id: int) -> Users:
    return Users.query.get_or_404(user_id)


def sort_and_paginate_questions(request_args: dict, direction: str = 'asc') -> Question:
    page = int(request_args.get('page', 1))
    order_by = request_args.get('order_by', 'submission_time')
    questions = "Question.query.order_by(Question.{}.{}())".format(order_by, direction)
    return eval(questions).paginate(page, per_page=10)


def fetch_questions_by_tag(request_args: dict) -> Question:
    order_by = request_args.get('order_by', 'submission_time')
    order_direction = request_args.get('order_direction', 'desc')
    page = int(request_args.get('page', int(1)))
    tag_id = int(request_args.get('tag_id'))
    filter_questions = "Question.query.filter_by(tag_id={}).order_by(Question.{}.{}())".format(tag_id, order_by, order_direction)
    return eval(filter_questions).paginate(page, per_page=10)


def search_query(request_args: dict) -> Question:
    order_by = request_args.get('order_by', 'submission_time')
    order_direction = request_args.get('order_direction', 'desc')
    search_phrase = request_args.get('search_phrase')
    page = int(request_args.get('page', 1))
    search_base = 'Question.query.filter(or_(func.lower(Question.title).like(func.lower(f"%{search_phrase}%")),func.lower(Question.message).like(func.lower(f"%{search_phrase}%"))))'
    order_direction = '.order_by(Question.{}.{}())'.format(order_by, order_direction)
    full_search_query = search_base + order_direction
    return eval(full_search_query).paginate(page, per_page=10)


def find_answers_and_all_related_by_user_id(user_id: int):
    return db.engine.execute("""
    SELECT answer.answer_id as answer_answer_id,
        answer.submission_time as asnwer_submission_time,
        answer.vote_number as vote_number,
        answer.question_id as answer_question_id, 
        answer.message as answer_message, 
        answer.user_id as answer_user_id,
        question.question_id as question_question_id, 
        question.user_id as question_user_id, 
        question.submission_time as question_submission_time,
        question.view_number as question_view_number, 
        question.vote_number as question_vote_number, question.title as question_title,
        question.message as question_message, 
        question.tag_id as question_tag_id, 
       (SELECT tag.tag_name FROM tag WHERE tag.tag_id = question.tag_id) as tag_name,
       (SELECT count(comment_for_answer.comment_id) FROM comment_for_answer WHERE comment_for_answer.answer_id = answer.answer_id) as count_comment
        FROM answer INNER JOIN question ON (answer.question_id = question.question_id) 
        WHERE answer.user_id = %(user_id)s ORDER BY answer.submission_time DESC;""", {'user_id': user_id})


def find_questions_by_user_id(user_id: int):
    return db.engine.execute("""
    SELECT question.question_id as question_id,
       question.user_id as question_user_id,
       question.submission_time as question_submission_time,
       question.edit_submission_time as question_edit_submission_time,
       question.view_number as question_view_number,
       question.vote_number as vote_number,
       question.title as question_title,
       question.message as question_message,
       question.tag_id as question_tag_id,
       (SELECT tag.tag_name FROM tag WHERE tag.tag_id = question.tag_id) as tag_name,
       (SELECT count(comment_for_question.comment_id) FROM comment_for_question WHERE comment_for_question.question_id = question.question_id) as count_comment,
       (SELECT count(answer.answer_id) FROM answer WHERE answer.question_id = question.question_id) as count_answer
    FROM question WHERE user_id =  %(user_id)s ORDER BY submission_time DESC;""", {'user_id': user_id})


def find_comments_for_questions_by_user_id(user_id: int):
    return db.engine.execute("""
    SELECT comment_for_question.comment_id as comment_id, comment_for_question.user_id as user_id,
       comment_for_question.question_id as comment_question_id, comment_for_question.message as message,
       comment_for_question.submission_time as submission_time, comment_for_question.edited_number as edited_number,
       (SELECT question.question_id as question_id FROM question WHERE question.question_id = comment_for_question.question_id),
       (SELECT question.title as question_title FROM question WHERE question.question_id = comment_for_question.question_id),
       (SELECT question.vote_number as question_vote_number FROM question WHERE question.question_id = comment_for_question.question_id),
       (SELECT  question.tag_id as question_tag_id FROM question WHERE question.question_id = comment_for_question.question_id)
    FROM comment_for_question WHERE comment_for_question.question_id NOTNULL AND comment_for_question.user_id =  %(user_id)s ORDER BY comment_for_question.submission_time DESC;""",
         {'user_id': user_id})


def find_comments_for_answers_by_user_id(user_id: int):
    return db.engine.execute("""
    SELECT comment_for_answer.comment_id as comment_id, comment_for_answer.user_id as user_id,
       comment_for_answer.question_id as comment_question_id, comment_for_answer.answer_id as answer_id, comment_for_answer.message as message,
       comment_for_answer.submission_time as submission_time, comment_for_answer.edited_number as edited_number,
       (SELECT question.question_id as question_id FROM question WHERE question.question_id = comment_for_answer.question_id),
       (SELECT question.title as question_title FROM question WHERE question.question_id = comment_for_answer.question_id),
       (SELECT question.vote_number as question_vote_number FROM question WHERE question.question_id = comment_for_answer.question_id),
       (SELECT  question.tag_id as question_tag_id FROM question WHERE question.question_id = comment_for_answer.question_id)
    FROM comment_for_answer WHERE comment_for_answer.answer_id NOTNULL AND comment_for_answer.user_id =  %(user_id)s ORDER BY comment_for_answer.submission_time DESC;""",
     {'user_id': user_id})

