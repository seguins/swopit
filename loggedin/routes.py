from webapp2_extras.routes import RedirectRoute

from loggedin import handlers as handlers

_routes = [
  RedirectRoute('/logout', handlers.LogoutHandler, name='logout', strict_slash=True)
]

def add_routes(app):
  for r in _routes:
    app.router.add(r)