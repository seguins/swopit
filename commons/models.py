# -*- coding: utf-8 -*-
import time
from webapp2_extras.appengine.auth.models import User
from google.appengine.ext import ndb
from webapp2_extras import security

global categories
categories = ["Salon", "Cuisine", "Chambre", "Bureau", "Salle de bain", "Petit décoration", "Equipement loisirs"]


class User(User):
  email_address = ndb.StringProperty(indexed=True)
  number_card = ndb.StringProperty(indexed=True)
  lastname = ndb.StringProperty(indexed=False)
  firstname = ndb.StringProperty(indexed=False)
  phone = ndb.StringProperty(indexed=False)
  displayPhone = ndb.BooleanProperty(default=True)
  token = ndb.StringProperty()

  def set_password(self, raw_password):
    self.password = security.generate_password_hash(raw_password, length=12)

  @classmethod
  def get_by_auth_token(cls, user_id, token, subject='auth'):
    token_key = cls.token_model.get_key(user_id, subject, token)
    user_key = ndb.Key(cls, user_id)
    valid_token, user = ndb.get_multi([token_key, user_key])
    if valid_token and user:
      timestamp = int(time.mktime(valid_token.created.timetuple()))
      return user, timestamp

    return None, None

  @classmethod
  def user_exist(cls, email):
    user = cls.query(cls.email_address == email).fetch(1)
    return len(user) == 1

  @classmethod
  def get_user(cls, email):
    user = cls.query(cls.email_address == email).fetch(1)
    if len(user) == 1:
      return user[0]
    return None

  @classmethod
  def user_by_token(cls, token):
    user =  cls.query(cls.token == token).fetch(1)
    if len(user) == 1:
      return user[0]
    return None


class Ad(ndb.Model):
  user = ndb.KeyProperty(kind='User')
  title = ndb.StringProperty()
  info = ndb.TextProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  image = ndb.BlobProperty()
  category = ndb.IntegerProperty()