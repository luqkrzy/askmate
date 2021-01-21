import inspect
from askmate import os, db, app_config
from secrets import token_hex
from PIL import Image
from askmate.models import Users, Tag, Question, QuestionTag, Answer, Comment


def set_picture_path(called_function):
    usr_pic_path = app_config['USR_PIC_PATH']
    question_pic_path = app_config['QUESTION_PIC_PATH']
    answer_pic = app_config['ANSWER_PIC']
    pic_path = app_config['PIC_PATH']
    if called_function == 'route_register':
        pic_path = usr_pic_path

    elif called_function == 'route_add_question' or called_function == 'route_edit_question':
        pic_path = question_pic_path

    elif called_function == 'route_add_answer':
        pic_path = answer_pic

    return os.path.join(os.getcwd(), pic_path)


def save_picture(form_picture):
    called_function = inspect.stack()[1].function
    random_hex = token_hex(6)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    full_picture_path = os.path.join(set_picture_path(called_function), picture_filename)
    output_size = (300, 200)
    pic = Image.open(form_picture)
    pic.thumbnail(output_size)
    pic.save(full_picture_path)
    return picture_filename


def switch_asc_desc(order_direction):
    return 'desc' if order_direction == 'asc' else 'asc'


def commit_to_database(data):
    db.session.add(data)
    db.session.commit()


def update_to_database():
    db.session.commit()


def register_new_user(new_user: dict):
    user = Users(user_name=new_user['user_name'], email=new_user['email'], password=new_user['password'], picture=new_user['picture'])
    commit_to_database(user)


def ask_new_question(new_question):
    question = Question(user_id=new_question['user_id'], title=new_question['title'], message=new_question['message'], image=new_question['image'], tag_id=new_question['tag_id'])
    commit_to_database(question)


def find_user_by_email(email):
    return Users.query.filter_by(email=email).first()


def fetch_tags():
    return Tag.query.all()


def get_all_tag_names():
    return [tag.tag_name for tag in list(fetch_tags())]


def count_tags():
    return db.engine.execute('SELECT tag_name, COUNT(tag.tag_id) FROM tag, question_tag WHERE tag.tag_id = question_tag.tag_id GROUP BY tag.tag_id;')


def choice_query():
    return Tag.query


def find_question_by_id(question_id):
    return Question.query.get_or_404(question_id)


def find_tag_name_by_id(tag_id):
    return Tag.query.filter_by(tag_id=tag_id).first()


def find_question_tag_by_id(question_id):
    return QuestionTag.query.filter_by(question_id=question_id).first()
    # return db.engine.execute('SELECT tag_id FROM question_tag WHERE question_id=124;')


def paginate_questions(page):
    return Question.query.paginate(page, per_page=10)


def count_answers_by_question_id(question_id):
    return Answer.query.filter_by(question_id=question_id).count()


def count_comments_by_question_id(question_id):
    return Comment.query.filter_by(question_id=question_id).count()


def count_comments_by_answer_id(answer_id):
    return Comment.query.filter_by(answer_id=answer_id).count()



def find_user_by_id(user_id):
    return Users.query.get_or_404(user_id)

def count_all_questions():
    return Question.query.count()


def sort_and_paginate_questions(page, order_by= 'title', direction = 'desc'):
    question = "Question.query.order_by(Question.{}.{}())".format(order_by, direction)
    return eval(question).paginate(page, per_page=10)


def paginate_questions_by_tag(page, tag_id, order_by='title', direction ='desc'):
    filter_question = "Question.query.filter_by(tag_id={}).order_by(Question.{}.{}())".format(tag_id, order_by, direction)
    return eval(filter_question).paginate(page, per_page=10)
