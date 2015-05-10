from commons.base_handler import *
from commons.models import *
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb, db
import math

class ListHandler(BaseHandler):
  NUMBER_ELEMENT_PER_PAGE = 2
  def get(self, page_number, category = -1):
    if page_number != None:
      page_number = int(page_number.replace("/", ""))
    else:
      page_number = 0
    offset = page_number * self.NUMBER_ELEMENT_PER_PAGE;
    if category == -1:
      query = Ad.query().order(-Ad.created)
    else:
      query = Ad.query(Ad.category == int(category)).order(-Ad.created)
    ads = query.fetch(self.NUMBER_ELEMENT_PER_PAGE, offset=offset)

    for ad in ads:
      if ad.user != None:
        u = ad.user.get()
        ad.email = u.email_address
        ad.phone = u.phone

    param = {
      'ads': ads,
      'current_page': page_number + 1,
      'category': int(category),
      'pages': range(1, int(math.ceil(float(query.count()) / float(self.NUMBER_ELEMENT_PER_PAGE))) + 1)
    }
    if category != -1:
      param["categoryStr"] = models.categories[int(category)];

    self.render_template('list.html', param)

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
    category = self.request.get('category')

    # Get image data
    image = self.request.get('file')
    # Transform the image
    image = images.resize(image, 250, 320)
    
    # Create and save into datastore
    print category
    print models.categories
    print models.categories.index(category)
    ad = Ad(title=title, info=info, image=image, user=self.user.key, category=categories.index(category))
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
        self.response.headers['Cache-Control'] = 'max-age=31536000'
        self.response.out.write(greeting.image)
    else:
        self.response.out.write('No image')

class ManageHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect('/')

class FilterHandler(BaseHandler):
  @user_required
  def post(self):
    self.redirect('/list/0/' + str(models.categories.index(self.request.get('category'))))