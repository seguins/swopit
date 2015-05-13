# -*- coding: utf-8 -*-
from commons.base_handler import *
from commons.models import *
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb, db
from google.appengine.api import mail

import math

NUMBER_ELEMENT_PER_PAGE = 5

class ListHandler(BaseHandler):
  def get(self, page_number, category = -1):
    if page_number != None:
      page_number = int(page_number.replace("/", ""))
    else:
      page_number = 0
    offset = page_number * NUMBER_ELEMENT_PER_PAGE;
    if category == -1:
      query = Ad.query().order(-Ad.created)
    else:
      query = Ad.query(Ad.category == int(category)).order(-Ad.created)
    ads = query.fetch(NUMBER_ELEMENT_PER_PAGE, offset=offset)
    for ad in ads:
      if ad.user != None:
        u = ad.user.get()
        ad.email = u.email_address
        ad.phone = u.phone
        ad.displayPhone = u.displayPhone
    param = {
      'ads': ads,
      'current_page': page_number + 1,
      'category': int(category),
      'pages': range(1, int(math.ceil(float(query.count()) / float(NUMBER_ELEMENT_PER_PAGE))) + 1)
    }
    if category != -1:
      param["categoryStr"] = models.categories[int(category)];

    self.render_template('list.html', param)


class ManageHandler(BaseHandler):
  @user_required
  def get(self, page_number):
    if page_number != None:
      page_number = int(page_number.replace("/", ""))
    else:
      page_number = 0
    offset = page_number * NUMBER_ELEMENT_PER_PAGE;
    query = Ad.query(Ad.user == self.user.key).order(-Ad.created)
    ads = query.fetch(NUMBER_ELEMENT_PER_PAGE, offset=offset)
    for ad in ads:
      if ad.user != None:
        u = ad.user.get()
        ad.email = u.email_address
        ad.phone = u.phone
        ad.displayPhone = u.displayPhone
    param = {
      'ads': ads,
      'current_page': page_number + 1,
      'manage': True,
      'pages': range(1, int(math.ceil(float(query.count()) / float(NUMBER_ELEMENT_PER_PAGE))) + 1)
    }
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

    try:
      # Transform the image
      image = images.resize(image, 250, 320)
    except images.Error:
      image = None
    # Create and save into datastore
    ad = Ad(title=title, info=info, image=image, user=self.user.key, category=int(category))

    if not ad.valide():
      upload_url = blobstore.create_upload_url('/createPhoto')
      self.render_template('create.html', {'upload_url': upload_url, 'failed': ad})
      return
    ad.put()
    
    # Redirect to the product page
    self.redirect('/manage')


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

class FilterHandler(BaseHandler):
  @user_required
  def post(self):
    self.redirect('/list/0/' + str(models.categories.index(self.request.get('category'))))

class DeleteHandler(BaseHandler):
  @user_required
  def get(self, urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    ad = key.get()
    if ad.user == self.user.key:
      key.delete()
    self.redirect('/manage/')

class ReportHandler(BaseHandler):
  @user_required
  def get(self, urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    ad = key.get()
    if ad.user == self.user.key:
      message = mail.EmailMessage()
      message.sender = "stephseguin93@gmail.com"
      message.to = "stephseguin93@gmail.com"
      message.subject = "Signalement d'une annonce"
      message.body = """
L'annonce "%s" vient d'être reportée par %s

Lien de l'annonce : %s/edit/%s
    """ % (str(ad.title), str(self.user.email_address), self.request.url.rsplit('/', 2)[0], urlsafe)
      print(message.body)
      message.send()
    self.redirect('/')


class EditHandler(BaseHandler):
  @user_required
  def get(self, urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    ad = key.get()
    if ad.user == self.user.key:
      self.render_template('create.html', {'ad': ad})
    else:
      self.redirect('/')

  @user_required
  def post(self, urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    ad = key.get()
    if ad.user == self.user.key:
      # Get informations
      ad.info = self.request.get('info')
      ad.title = self.request.get('title')
      ad.category = int(self.request.get('category'))
      ad.put()
    
    self.redirect('/')

class ProfileHandler(BaseHandler):
  @user_required
  def get(self):
    self.render_template('signup.html', {'userEdition': self.user})
  def post(self):
    u = self.user
    u.email_address = self.request.get('email')
    u.username = self.request.get('email')
    u.set_password(self.request.get('password'))
    u.number_card = self.request.get('number_card')
    u.lastname = self.request.get('lastname')
    u.firstname = self.request.get('firstname')
    u.phone = self.request.get('phone')
    u.displayPhone = (self.request.get('displayNumber') != 'on')

    if not u.valide():
      self.render_template('signup.html', { 'failed': u, 'userEdition': self.user });
      return

    u.put()

    self.auth.get_user_by_password(u.username, self.request.get('password'), remember=True, save_session=True)


    self.redirect('/')