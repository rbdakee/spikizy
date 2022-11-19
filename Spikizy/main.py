from flask import Flask, render_template, url_for, request, redirect, flash, session
import itsdangerous
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy
from db import db, Users
from send_link import send_link

# создаем конфигурации для использования Flask_sqlalchemy и самого flask
app = Flask(__name__)
s = URLSafeTimedSerializer('AJFBk121nvpasUBfaf92pnv02vdjsvb200we0wiesfj')
app.config["SECRET_KEY"] = 'JAsd920whcsUSbsajwq09329bsIUabsdf8q20s'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/') # Это у нас роутеры, то есть ссылки при которых будут выполняться действия из функции ниже
def index():
    if 'userName' in session:
        return render_template('index_authorized.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['Email']   # Мы берем значения из нашей формы в login page
        password = request.form['Password']
        user = Users.loginning(email, password)
        if type(user)==None:
            flash("Неправильный логин или пароль! Повторите попытку.")      # Возвращаем сообщение
        elif type(user)==list:
            session['userName']=user[0]
            session['userEmail']=user[1]
            return redirect(url_for('index')) # Перенаправляем в index page
    return render_template('login.html')


@app.route('/registration', methods = ['POST', 'GET'])
def registration():
    if request.method == 'POST':
        user = Users.registration(request.form['Name'], request.form['Email'], request.form['Password'])     # Регистрируем нового пользователя
        return redirect(url_for('login')) # Перенаправляем в login page
    return render_template('signup.html')

@app.route('/forgot', methods=['POST','GET'])
def xlogin():
    if request.method=="POST":
        user_email = request.form['uname']
        token = s.dumps(user_email, salt='email-confirm')
        message = f'Это письмо было отправлено для сброса пароля на сайте spikizy.kz пользователя с электронным адресом "{user_email}"\nЕсли вы не хотите изменять пароль, не открывайте ссылку и не отправляйте ее никому\n' + url_for('confirm_email', token=token, email=user_email, _external=True)
        send_link(message, user_email)

    return render_template('forgot.html')

@app.route('/confirm_email/<token>/<email>', methods=['POST', 'GET'])
def confirm_email(token, email):
    if request.method=='POST':
        new_psw = request.form['newpsw']
        email = request.form['email']
        Users.update_psw(email, new_psw)
        return redirect(url_for('login'))
    try:
        s.loads(token, salt='email-confirm', max_age=600)
    except (itsdangerous.exc.SignatureExpired, itsdangerous.exc.BadTimeSignature, itsdangerous.exc.BadSignature):
        return render_template('expired_token.html')
    return render_template('changePassword.html', email = email, token=token )

@app.route('/update_password', methods=['POST', 'GET'])
def update_password():
    if request.method=='POST':
        new_psw = request.form['newpsw']
        email = request.form['email']
        Users.update_psw(email, new_psw)
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('userEmail', None)
    session.pop('userName', None)
    return redirect(url_for('index'))


# Нужно для дебаггинга сервера
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')