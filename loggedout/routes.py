from webapp2_extras.routes import RedirectRoute

from loggedout import handlers as handlers

_routes = [
  RedirectRoute('/', handlers.MainHandler, name='home', strict_slash=True),
  RedirectRoute('/signin', handlers.SigninHandler, name='signin', strict_slash=True),
  RedirectRoute('/signup', handlers.SignupHandler, name='signup', strict_slash=True),
  RedirectRoute('/login', handlers.LoginHandler, name='login', strict_slash=True)
]


def add_routes(app):
  for r in _routes:
    app.router.add(r)