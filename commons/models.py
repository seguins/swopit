# -*- coding: utf-8 -*-
import time
from webapp2_extras.appengine.auth.models import User
from google.appengine.ext import ndb
from webapp2_extras import security

from google.appengine.api import mail


global categories
categories = ["Salon", "Cuisine", "Chambre", "Bureau", "Salle de bain", "Petite décoration", "Equipement loisirs"]


class User(User):
  email_address = ndb.StringProperty(indexed=True, required=True)
  number_card = ndb.StringProperty(indexed=True, required=True)
  lastname = ndb.StringProperty(indexed=False, required=True)
  firstname = ndb.StringProperty(indexed=False, required=True)
  phone = ndb.StringProperty(indexed=False, required=True)
  displayPhone = ndb.BooleanProperty(default=True, required=True)
  token = ndb.StringProperty()

  def set_password(self, raw_password):
    self.password = security.generate_password_hash(raw_password, length=12)

  def valide(self):
    good = True
    if not self.email_address or not mail.is_email_valid(self.email_address):
      self.error_email = True
      good = False
    if not self.number_card:
      self.error_number_card = True
      good = False
    if not self.lastname:
      self.error_lastname = True
      good = False
    if not self.firstname:
      self.error_firstname = True
      good = False
    if not self.phone :
      self.error_phone = True
      good = False
    return good

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
  title = ndb.StringProperty(required=True)
  info = ndb.TextProperty(required=True)
  created = ndb.DateTimeProperty(auto_now_add=True)
  image = ndb.BlobProperty(required=True)
  category = ndb.IntegerProperty(required=True)

  def valide(self):
    good = True
    if not self.title:
      self.error_title = True
      good = False
    if not self.info:
      self.error_info = True
      good = False
    if not self.image:
      self.error_image = True
      good = False
    return good
