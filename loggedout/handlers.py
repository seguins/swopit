# -*- coding: utf-8 -*-
from commons.base_handler import BaseHandler
from commons.models import *

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from google.appengine.api import mail

import uuid

class LoginHandler(BaseHandler):
  def get(self):
    self._serve_login()

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    try:
      u = self.auth.get_user_by_password(username, password, remember=True,
        save_session=True)
      self.redirect(self.uri_for('home'))
    except (InvalidAuthIdError, InvalidPasswordError) as e:
      self._serve_login(True)

  def _serve_login(self, failed=False):
    username = self.request.get('username')
    params = {
      'username': username,
      'failed': failed
    }
    self.render_template('login.html', params)

class SignupHandler(BaseHandler):
  def get(self):
    self.render_template('signup.html')

  def post(self):
    email = self.request.get('email')
    password = self.request.get('password')
    number_card = self.request.get('number_card')
    lastname = self.request.get('lastname')
    firstname = self.request.get('firstname')
    phone = self.request.get('phone')
    displayPhone = (self.request.get('displayNumber') != 'on')

    u = User(email_address=email, password_raw=password,
      number_card=number_card, lastname=lastname, firstname=firstname,
      phone=phone, displayPhone=displayPhone)

    if not u.valide():
      self.render_template('signup.html', { 'failed': u });
      return

    unique_properties = ['email_address']
    user_data = self.user_model.create_user(email,
      unique_properties,
      email_address=email, password_raw=password,
      number_card=number_card, lastname=lastname, firstname=firstname,
      phone=phone, displayPhone=displayPhone, verified=True)
    if not user_data[0]:
      u.alreadyUsed = True
      u.error_email = True
      self.render_template('signup.html', {'failed': u})
      return
    
    user = user_data[1]

    self.redirect('/')

class SigninHandler(BaseHandler):
  def post(self):
    username = self.request.get('username')
    self.session.add_flash(username)
    if (self.user_model.user_exist(username) != False):
      self.redirect('/login')
    else:
      self.redirect('/signup')

class LegalHandler(BaseHandler):
  def get(self):
    self.render_template('legal.html')

class AboutHandler(BaseHandler):
  def get(self):
    self.render_template('about.html')

class MainHandler(BaseHandler):
  def get(self):
    if not self.auth.get_user_by_session():
      self.render_template('index.html')
    else:
      self.render_template('choice.html')

class ForgetHandler(BaseHandler):
  def get(self):
    self.render_template("forget.html")
  
  def post(self):
    username = self.request.get('username')
    user = self.user_model.get_user(username)
    if (user != None):
      token = str(uuid.uuid4())
      user.token = token
      user.put()

      message = mail.EmailMessage()
      message.sender = "stephseguin93@gmail.com"
      message.to = username
      message.subject = "Mot de passe oublié"
      message.body = """
Vous avez oublié votre mot de passe pour Stan'Ton Meuble.

Cliquer sur le lien suivant pour le réinitialiser votre mot de passe : 
%s/%s
    """ % (self.request.url, token)
      message.send()
    self.redirect("/")

class NewForgetHandler(BaseHandler):
  def get(self, token):
    u = User.user_by_token(token)
    if u == None:
      self.notfound()
    else:
      self.render_template("newForget.html")
  
  def post(self, token):
    password = self.request.get('password')
    u = User.user_by_token(token)
    if u == None:
      self.notfound()
    else:
      u.set_password(password)
      u.token = None
      u.put()
      self.redirect("/")