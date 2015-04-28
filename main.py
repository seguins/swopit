import webapp2

from loggedout import routes as loggedout_routes
from loggedin import routes as loggedin_routes

config = {
  'webapp2_extras.auth': {
    'user_model': 'commons.models.User',
    'user_attributes': ['email_address']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}


application = webapp2.WSGIApplication(debug=True, config=config)

loggedout_routes.add_routes(application)
loggedin_routes.add_routes(application)