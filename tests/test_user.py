import os
import json
from .cuteBaseTest import CuteBaseTest

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')


class TestUser(CuteBaseTest):
    """ test various actions on the user resource """
    supervisor = {
        "email": "wapi.niwapi@gmail.com",
        "role": "supervisor"
    }

    admin = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }

    activate_supervisor = {
        "password": "genomeshotgun",
        "isActive": True
    }

    def create_admin(self):
        """  admin creating function """
        response = self.client.get(
            '/admin',
            content_type="application/json"
        )
        return response

    def signin_admin(self):
        """ signin admin"""
        response = self.client.post(
            '/users/login',
            data=json.dumps(self.admin),
            content_type="application/json"
        )
        return response

    def create_supervisor(self, admin_token):
        """ user creation function """
        response = self.client.post(
            '/users/create',
            data=json.dumps(self.supervisor),
            headers={'auth_token': admin_token},
            content_type="application/json"
        )
        return response

    def test_creating_admin(self):
        """ test creating an admin"""
        response = self.create_admin()
        self.assertEqual(response.status_code, 201)

        duplicate_admin_resp = self.create_admin()
        self.assertEqual(duplicate_admin_resp.status_code, 409)

    def test_creating_supervisor(self):
        """ test creating a user and activating their account """
        admin_creation_resp = self.create_admin()
        self.assertEqual(admin_creation_resp.status_code, 201)

        admin_login_resp = self.signin_admin()
        self.assertEqual(admin_login_resp.status_code, 200)

        admin_token = admin_login_resp.json['data']['auth_token']
        sup_creation_resp = self.create_supervisor(admin_token)
        self.assertEqual(sup_creation_resp.status_code, 201)


        







