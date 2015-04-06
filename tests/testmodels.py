import unittest
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from commons import models

class UserTestCase(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testInsertEntity(self):
    models.User.put(models.User())
    self.assertEqual(1, len(models.User.query().fetch(2)))

  def testExistUser(self):
    models.User.put(models.User(number_card="12345"))
    self.assertEqual(1, len(models.User.query().fetch(2)))
    self.assertEqual(True, models.User.user_exist("12345"))
    self.assertEqual(False, models.User.user_exist("123"))

if __name__ == '__main__':
  unittest.main()
