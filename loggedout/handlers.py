from commons.base_handler import BaseHandler
import commons.models

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
      logging.info('Login failed for user %s because of %s', username, type(e))
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
    user_name = self.request.get('username')
    email = self.request.get('email')
    password = self.request.get('password')
    number_card = self.request.get('number_card')

    unique_properties = ['email_address']
    user_data = self.user_model.create_user(user_name,
      unique_properties,
      email_address=email, username=user_name, password_raw=password,
      number_card=number_card, verified=True)
    if not user_data[0]: #user_data is a tuple
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Unable to create user for email %s because of \
        duplicate keys %s' % (user_name, user_data[1]))
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

class MainHandler(BaseHandler):
  def get(self):
    if not self.auth.get_user_by_session():
      self.render_template('index.html')
    else:
      self.render_template('list.html')
