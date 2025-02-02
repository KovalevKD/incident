from re import S
from flask import url_for, g

from datetime import datetime
# from flask_login import UserMixin
# from flask_security import RoleMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


# from app import db


class roles_users(db.Model):
    __tablename__ = 'roles_user'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String)
    user_id =  db.Column(db.Integer(), db.ForeignKey("user.id"))
    role_id =  db.Column(db.Integer(), db.ForeignKey("roles.id"))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    users = relationship("User", secondary="roles_user", back_populates='roles')

    def __str__(self):
        return self.name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    # Нужен для security!
    active = db.Column(db.Boolean())
    # Для получения доступа к связанным объектам
    roles = relationship("Role", secondary="roles_user", back_populates='users')

    # Flask - Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # Flask-Security
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)