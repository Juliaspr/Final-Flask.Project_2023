from flask_mail import Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import render_template, request, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required

from sqlalchemy import func
from logic import get_concate_username
from OAuth import OAuthSignIn

import models
from forms import LoginForm, RegistrationForm, DescriptionForm
from app import app, db, mail
from models import User, friends


@app.route('/')
def index():  # put application's code here
    userTest = {"username": 'You need to registrate'}
    posts = [
        {
            'author': {'username': 'Save your password'},
            'head': "You need to registrate",
            'body': "Complete your profile"
        }
    ]
    # send_mail("email")
    return render_template('Index.html', title="Main", user=userTest, posts=posts)


@app.route('/CheckUp')
@login_required
def CheckUp():
    username = {"fio": 'Спиридонова Юлия Вячеславовна'}
    return '''
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <title>Title</title>
      </head>
<body>
  <h2>Hello</h2><h2>''' + username["fio"] + '''</h2>
</body>
</html>
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect((url_for("index")))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect((url_for("index")))
        login_user(user, remember=True)
        return redirect((url_for("index")))
    return render_template("login.html", form=form)


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    user_id, token = oauth.callback()
    if user_id is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        username = get_concate_username(token, user_id)

        user = User(user_id=user_id, token=token, username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user, True)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect((url_for("index")))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats! Registration is completed!')
        return redirect((url_for('login')))
    return render_template("registration.html", form=form)


def send_mail(address):
    with mail.connect() as conn:
        msg = Message("Test message", sender="Your Email", recipients=[address])
        msg.body = "Hello boddy"
        msg.html = "<h1>Test</h1>"
        conn.send(msg)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect((url_for("index")))


@app.route('/profile')
def profile():
    engine = create_engine("mysql+pymysql://root:root@localhost/myflaskdb", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = User.query.filter_by(username=current_user.username).first()
    num = session.query(func.count(user_id=current_user.id)).select_from(friends).filter_by(user_id=current_user.id).all()
    return render_template('profile.html', title="Profile", num=num, user=user)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = DescriptionForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        user.set_phone(phone=form.phone.data)
        user.set_description(description=form.description.data)
        user.set_email(email=form.email.data)
        db.session.commit()
        return redirect((url_for('profile')))
    return render_template('description.html', title="Settings", form=form)


@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('UsersList.html', users=all_users)


@app.route('/add_friend/<username>')
def add_friend(username):
    user = User.query.filter_by(username=username).first()
    if not user is None:
        current_user.add_friend(user)
        db.session.commit()
    all_users = User.query.all()
    return render_template('UsersList.html', users=all_users)


@app.route('/remove_friend/<username>')
def remove_friend(username):
    user = User.query.filter_by(username=username).first()
    if not user is None:
        current_user.delete_friend(user)
        db.session.commit()
    all_users = User.query.all()
    return render_template('UsersList.html', users=all_users)


@app.route('/friends/')
@login_required
def show_friends():
    all_users = User.query.all()
    return render_template('friends.html', users=all_users)


@app.route('/usersprofile/<username>')
@login_required
def users_profile(username):
    engine = create_engine("mysql+pymysql://root:root@localhost/myflaskdb", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = User.query.filter_by(username=username).first()
    num = session.query(func.count(user_id=user.id)).select_from(friends).filter_by(user_id=user.id).all()
    return render_template('usersprofile.html', user=user, num=num)