from checkepisode import db
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy.ext.associationproxy import association_proxy

watched_episodes = db.Table('watched_episodes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('episode_id', db.Integer, db.ForeignKey('episode.id'))
)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(120))
    active = db.Column(db.Boolean())
    confirmation_token = db.Column(db.String(255))
    confirmation_sent_at = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    favorite_series = association_proxy('user_series', 'serie')
    watched_episodes = db.relationship('Episode', secondary=watched_episodes,
        backref=db.backref('users', lazy='dynamic'))
