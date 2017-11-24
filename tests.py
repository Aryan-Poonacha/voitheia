#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User


#explanations
'''

#it may have subclasses, each of which is a different set of test cases
class TestCase(unittest.TestCase):

    #statements in setUp are executed before each test case
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    #statements in tearDown are executed after each test case
    def tearDown(self):
        db.session.remove()
        db.drop_all()


    #each different test case is executed as a different function
    def test_avatar(self):
        u = User(username='abcd', email='c@d.com', password="1234", id = '3')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/%s?d=mm&s=%d'
        assert avatar[0:len(expected)] == expected
'''



class TestCase(unittest.TestCase):
    #...
    def test_follow(self):
        u1 = User(id = 3,username='john', email='john@example.com', password = '123')
        u2 = User(id = 2,username='susan', email='susan@example.com', password = '1234')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().username == 'susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().username == 'john'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

if __name__ == '__main__':
    unittest.main()