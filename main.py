from flask import Flask, redirect, url_for, session, jsonify, render_template, request, flash
from flask_paginate import Pagination, get_page_args
from flask_login import LoginManager, login_user, login_required, logout_user
import datetime
from config import *
import random
import time
import string
import os
from flask_session import Session
import uuid
from getmac import get_mac_address
from bd import BD
from models.user import User, db
from api import *
from commands import *
from threading import Thread
from decorators import role_required

ALLOWED_GRADES = ('2', '3', '4', '5', 'н', 'у', '')

bd = BD()

lessons = None

app = Flask(__name__)
app.secret_key = 'dammn'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://psgadammn:pogoda00@localhost/kursach'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

Session(app)


def send_email(subject, body, to_email):
    session['key_confirm'] = body
    os.system(f'echo "{body}" | /usr/bin/mail -s "{subject}" {to_email}')
    print("Письмо отправлено!")


@login_manager.user_loader
def load_user(user_id):
    return User(bd.oneSelectBD('users', {'id': user_id}))


def get_user():
    return bd.oneSelectBD('users', {'id':  session.get('user_id')})


@app.route('/')
def index():
    if not session.get('user_id'):
        session['user_id'] = str(uuid.uuid4())
    if not session.get('ip'):
        session['ip'] = request.headers.get('X-Forwarded-For', 'Не указано')
    if not session.get('mac'):
        session['mac'] = get_mac_address(ip=request.remote_addr)

    user = get_user()
    if user:
        if user['role'] == 'Студент':
            lessons_today = get_today_lessons(download_json(
                lessons[user['user_group']])) if user['user_group'] else {}
            return render_template('index.html', user=user, lessons=lessons_today)
        elif user['role'] == 'Родитель':
            children = [i for i in bd.selectBD(
                'parent_students') if i['parent'] == user['id']]
            children_lessons = []
            for child in children:
                child_info = bd.oneSelectBD('users', {'id': child['children']})
                if child_info:
                    lessons_today = get_today_lessons(
                        download_json(lessons[child_info['user_group']]))
                    children_lessons.append(
                        {child_info['firstname']: lessons_today if lessons_today else {}})
            return render_template('index.html', user=user, children_lessons=children_lessons,
                                   childrens=[list(i)[0] for i in children_lessons], count=range(len(children)))
        elif user['role'] == 'Админ':
            return render_template('index.html', user=user)
    return render_template('index.html', user=None)


@app.route('/confirm', methods=['POST'])
def confirm():
    confirmation_code = request.form.get('confirmation_code')
    if confirmation_code == session.get('key_confirm'):
        user_data = {
            'id': session.get('user_id'),
            'email': session.get('email_user'),
            'password': session.get('password'),
            'firstname': session.get('firstname'),
            'lastname': session.get('lastname'),
            'surname': session.get('surname'),
            'role': session.get('role'),
            'ip': session.get('ip')
        }
        bd.inputBD('users', **user_data)
        return redirect(url_for('login'))
    return ('', 204)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email_user = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        surname = request.form.get('surname')
        password = request.form.get('password')
        role = request.form.get('role')

        if bd.oneSelectBD('users', {'email': email_user}):
            flash('Пользователь с такой почтой уже существует', 'error')
            return '', 403

        gen_pswrd = ''.join(random.choices(
            string.ascii_letters + string.digits, k=10))
        send_email('Подтверждение регистрации MPT.net', gen_pswrd, email_user)

        session['user_id'] = str(uuid.uuid4())
        session['email_user'] = email_user
        session['firstname'] = firstname
        session['lastname'] = lastname
        session['surname'] = surname
        session['password'] = password
        session['role'] = role

        return '', 204

    return render_template('signup.html')


@app.route('/check_session')
@role_required(role='Админ', get_user=get_user)
def check_session():
    session_data = {key: session[key] for key in session.keys()}
    return jsonify(session_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = bd.oneSelectBD(
            'users', {'email': request.form['login'], 'password': request.form['password']})
        if user:
            login_user(User(user))
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    return render_template('auth.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/student/lessons')
def lessons_student():
    group = request.args.get('data')
    if group and group in lessons:
        return jsonify(download_json(lessons[group]))
    return render_template('lessons_student.html', groups=[i['title'] for i in bd.selectBD('groups')], user=get_user())


@app.route('/read_sessions')
@role_required(role='Админ', get_user=get_user)
def read_sessions():
    return jsonify(dict(get_user()))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_user()
    if request.method == 'POST':
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo:
                url_photo = f'static/images/{session["user_id"]}.png'
                photo.save(url_photo)
                bd.updateBD('users', {'photo':'/' + url_photo},
                            {'id': session['user_id']})
        password = request.form.get('password')
        group = request.form.get('group')
        if password:
            bd.updateBD('users', {'password': password},
                        {'id': session['user_id']})
        if group and group != user['user_group']:
            bd.updateBD('users', {'user_group': group}, {'id': session['user_id']})
        return redirect(url_for('profile'))
    return render_template('profile.html', groups=[i['title'] for i in bd.selectBD('groups')], user=user)


@app.route('/student/items')
@login_required
@role_required(role='Студент', get_user=get_user)
def student_items():
    user = get_user()
    items = [i for i in bd.selectBD(
        'items_groups') if user['user_group'] == i['group_title']]
    return render_template('student_items.html', items=items, user=user)


@app.route('/teacher/grades', methods = ['GET', 'POST'])
#@role_required('Преподаватель')
def grades():
      group = request.args.get('group')
      item = request.args.get('item')
      users = [i for i in bd.selectBD('users') if i['user_group'] == group]
      users_list = [i['id'] for i in users]
      grades = [i for i in bd.selectBD('grades') if i['user_id'] in users_list]
      dates = sorted(list(set([i['date'] for i in grades])), key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
      for i in users:
            dates_user = [d['date'] for d in grades if d['user_id'] == i['id'] and item == d['item_id']]
            if len(dates_user) != len(dates):
                  for j in dates:
                        if not j in dates_user:
                              bd.inputBD('grades', user_id=i['id'], item_id=item,date=j, grade = '')
      grades = [i for i in bd.selectBD('grades') if i['user_id'] in users_list]
      if request.method == 'POST':
            if datetime.datetime.today().strftime('%Y-%d-%m') in dates:
                  return '', 403
            for j in users:
                  bd.inputBD('grades', user_id=j['id'], item_id=item,date=datetime.today().strftime('%d.%m.%Y'), grade = '')
                  grades = [i for i in bd.selectBD('grades') if i['user_id'] in users_list]
                  dates = sorted(list(set([i['date'] for i in grades])), key=lambda x: datetime.strptime(x, "%Y-%m-%d"))

            return render_template('grades.html',
                  users = users,
                  item = item,
                  user = get_user(),
                  grades = grades,
                  dates = dates,
                  group = group
            ), 200
      return render_template('grades.html',
            users = users,
            item = item,
            user = get_user(),
            grades = grades,
            dates = dates,
            group = group
      )



@app.route('/updateGrade', methods=['POST'])
@login_required
#@role_required(role='Преподаватель', get_user=get_user)
def updateGrade():
    date = request.json.get('date')
    student_id = request.json.get('student_id')
    grade = request.json.get('grade')
    print(grade)
    if grade in ALLOWED_GRADES:
        bd.updateBD('grades',
                    {'grade': grade},
                    {'user_id':student_id, 'date':date})
        return '', 200
    return '', 403


@app.route('/admin_users', methods=['GET', 'POST', 'DELETE'])
@login_required
@role_required(role='Админ', get_user=get_user)
def admin_users():
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    users = bd.selectBD('users', limit=per_page, offset=offset)
    total_users = len(bd.selectBD('users'))
    pagination = Pagination(page=page, per_page=per_page,
                            total=total_users, css_framework='bootstrap4')

    if request.method == 'POST':
        id = request.form.get('user_id')
        firstname = request.form['firstname']
        surname = request.form['surname']
        lastname = request.form['lastname']
        role = request.form['user_role']
        group = request.form['group_user']
        email = request.form['email']
        password = request.form['password']

        if id != '':
            bd.updateBD('users',{
                'firstname' : firstname,
                'surname': surname,
                'lastname': lastname,
                'user_group' :group,
                'role': role,
                'email': email,
                'password': password},
                {'id':id}
            )
        else:
            id = str(uuid.uuid4())
            bd.inputBD('users',
                firstname=firstname,
                surname=surname,
                lastname=lastname,
                user_group=group,
                role=role,
                email=email,
                id=id,
                password=password)
        return redirect(url_for('admin_users'))

    if request.method == 'DELETE':
        delete_id = request.args.get('id')
        if delete_id:
            bd.deleteBD('users', id=delete_id)
            return redirect(url_for('admin_users'))

    return render_template('admin_users.html', users=users, page=page, per_page=per_page,
                           pagination=pagination, pages=list(pagination.pages), groups=[i['title'] for i in bd.selectBD('groups')], user=get_user())


@app.route('/parent_students', methods=['GET', 'POST', 'DELETE'])
@login_required
@role_required(role='Админ', get_user=get_user)
def parent_student():
    parents = [i for i in bd.selectBD('users') if i['role'] == 'Родитель']
    students = [i for i in bd.selectBD('users') if i['role'] == 'Студент']
    parent_students_list = bd.selectBD('parent_students')

    if request.method == 'POST':
        parent = request.form['parent_id']
        children = request.form['student_id']
        if not bd.oneSelectBD('parent_students', {'parent': parent, 'children': children}):
            bd.inputBD('parent_students', parent=parent, children=children)
            return redirect(url_for('parent_student'))
        return '', 403

    return render_template('parent_student.html', parents=parents, students=students, parent_students_list=parent_students_list, user=get_user())


def infinity_parse():
    global lessons
    while True:
        lessons = read_file('rp.json')
        write_file('rp.json', download())
        lessons = read_file('rp.json')
        time.sleep(60 * 15)


Thread(target=infinity_parse, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
