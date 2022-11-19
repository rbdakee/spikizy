from types import NoneType
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# создаем конфигурации для использования Flask_sqlalchemy и самого flask
app = Flask(__name__)
app.config["SECRET_KEY"] = 'JAsd920whcsUSbsajwq09329bsIUabsdf8q20s'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Прописываем команду ниже в терминале в том ре расположении файла, что и db.py файл, чтобы создать БД и таблицу со столбцами
'''
from db import db
db.create_all()
exit()
'''


# Это сама Таблица Users созданная с помощью db.Model
class Users(db.Model):
    # Здесь мы задаем какие значения и имена будут у столбцов, включая все признаки, как primary_key
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)      # email являетя unique элементом
    password = db.Column(db.String(500), nullable=False)
    accountType = db.Column(db.Integer)
    logo = db.Column(db.LargeBinary)

    # Эта функция нужна, чтобы инициализировать объект класса, получается, что мы с помощью __init__() регистрируем нового пользователя
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        db.session.add(self)
        db.session.commit()

    # функция loginning() нужна чтобы проверить введенные данные и сверить их с БД 
    # при введенных правильных данных функция вовзращает list со значениями username и email, чтобы позже использовать эти данные в сессии сайта
    # при неправильных введенных данных функция возвращает значение None, чтобы можно было понять уже на сервере, что нам возвратила функция
    def loginning(email, password):
        user = Users.query.filter_by(email=email, password=password).first()
        try:
            return [user.username, user.email]
        except AttributeError: 
            return None

    # Функция регистрации, с проверкой уникального элемента email
    # Нам нужна проверка уникального элемента, чтобы сервер не выдал ошибку при регистрации двух одинаковых email-ов, а чтобы просто возвратил сообщение 
    def registration(username, email, password):
        user = Users.query.filter_by(email=email).first()
        if type(user) == NoneType:
            user = Users(username=username, email=email, password=password)
            return f'Зарегестрирован новый пользователь {username}\nEmail: {email}'
        else:
            return 'Пользователь с таким Email уже существует!'


    def update_psw(email, new_password):
        user = Users.query.filter_by(email=email).first()
        user.password = new_password
        db.session.commit()
