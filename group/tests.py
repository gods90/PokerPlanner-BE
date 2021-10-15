from os import name
from django.urls import reverse

from ddf import G
from rest_framework.test import APITestCase

from group.models import Group
from user.models import User
from rest_framework.authtoken.models import Token

class GroupTestCases(APITestCase):
    """
    Group testcases for testing group list, details and add member functionality
    """
    GROUP_URL = reverse('group-list')

    def setUp(self):
        """
        Setup method for creating default user and it's token
        """
        self.user = G(User)
        token = G(Token, user=self.user)
        self.group = G(Group, created_by=self.user,name="newgroup")
        print(self.group)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_group(self):
        """
        Test case to create group with default user as logged in user.
        """
        data = {
            'name': 'csk'
        }
        response = self.client.post(self.GROUP_URL, data=data)
        print(response.data)
        group = Group.objects.get(name="csk")
        expected_data = {
            "id": group.id,
            "name": group.name,
            "created_by": self.user.id,
            "users": [
                {
                    "email": self.user.email,
                }
            ]
        }
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(expected_data, response.data)

    