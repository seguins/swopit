from commons.base_handler import BaseHandler
from commons.models import *

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

class LoginHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    try:
      u = self.auth.get_user_by_password(username, password, remember=True,
        save_session=True)
      self.redirect(self.uri_for('home'))
    except (InvalidAuthIdError, InvalidPasswordError) as e:
      self._serve_page(True)

  def _serve_page(self, failed=False):
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

    unique_properties = ['email_address']
    user_data = self.user_model.create_user(email,
      unique_properties,
      email_address=email, password_raw=password,
      number_card=number_card, lastname=lastname, firstname=firstname,
      phone=phone, verified=True)
    if not user_data[0]: #user_data is a tuple
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Unable to create user for email %s because of \
        duplicate keys %s' % (email, user_data[1]))
      return
    
    user = user_data[1]
    user_id = user.get_id()

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