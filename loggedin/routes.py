from webapp2_extras.routes import RedirectRoute

from loggedin import handlers as handlers

_routes = [
  RedirectRoute('/logout', handlers.LogoutHandler, name='logout', strict_slash=True),
  RedirectRoute('/create', handlers.CreateHandler, name='create', strict_slash=True),
  RedirectRoute('/filterCategory', handlers.FilterHandler, name='filter', strict_slash=True),
  ('/manage', handlers.ManageHandler),
  ('/list(/\d+)?', handlers.ListHandler),
  ('/list/(\d+)/(\d+)', handlers.ListHandler),
  ('/view/([^/]+)?', handlers.ViewHandler),
  ('/photo/([^/]+)?', handlers.ImageHandler)
]

def add_routes(app):
  for r in _routes:
    app.router.add(r)