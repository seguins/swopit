from commons.base_handler import *
from commons.models import Ad
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb, db

class LogoutHandler(BaseHandler):
  def get(self):
    self.auth.unset_session()
    self.redirect(self.uri_for('home'))

class CreateHandler(BaseHandler):
  @user_required
  def get(self):
    upload_url = blobstore.create_upload_url('/createPhoto')
    self.render_template('create.html', {'upload_url': upload_url})

  @user_required
  def post(self):
    
    # Get informations
    info = self.request.get('info')
    title = self.request.get('title')

    # Get image data
    image = self.request.get('file')
    # Transform the image
    image = images.resize(image, 1800, 200)
    
    # Create and save into datastore
    ad = Ad(title=title, info=info, image=image)
    ad.put()
    
    # Redirect to the product page
    self.redirect('/view/' + ad.key.urlsafe())

class ViewHandler(BaseHandler):
  @user_required
  def get(self, urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    ad = key.get()

    if ad == None:
      self.notFound()

    self.render_template('view.html', {
      'info': ad.info,
      'title': ad.title,
      'safe_image_url': '/photo/' + urlsafe
      })


class ImageHandler(webapp2.RequestHandler):
  def get(self, urlsafe):
    greeting_key = ndb.Key(urlsafe=urlsafe)
    greeting = greeting_key.get()
    if greeting.image:
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(greeting.image)
    else:
        self.response.out.write('No image')
