import unittest
from app import create_app
from app.api.models import db


class CuteBaseTest(unittest.TestCase):
    """ creating setup and teardown methods """
    def setUp(self):
        """running before all tests """
        self.app = create_app()
        self.app.config.from_object('config.TestingConfig')
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """ run after each test """
        db.session.remove()
        db.drop_all()