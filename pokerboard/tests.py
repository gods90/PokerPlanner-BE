import json
from ddf import G

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from group.models import Group
from user.models import User
from pokerboard.models import Pokerboard


class PokerboardTestCases(APITestCase):
    """
    Test case for pokerboard API
    """
    POKERBOARD_URL = reverse('pokerboard-list')

    def setUp(self):
        """
        Setup method for creating user and its token.
        """
        self.user = G(User, email="tv114@gmail.com")
        token = G(Token, user=self.user)
        self.pokerboard = G(Pokerboard, manager=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_pokerboard(self):
        """
        Create pokerboard give title and description
        """
        data = {
            'title': 'csk',
            'description': '4th time',
            "configuration": 3
        }
        response = self.client.post(self.POKERBOARD_URL, data=json.dumps(
            data), content_type="application/json")

        self.assertEqual(response.status_code, 201)
        pokerboard = Pokerboard.objects.get(id=response.data["id"])
        expected_data = {
            "id": pokerboard.id,
            "manager": pokerboard.manager.id,
            "title": pokerboard.title,
            "description": pokerboard.description,
            "configuration": pokerboard.configuration
        }
        self.assertDictEqual(expected_data, response.data)

    def test_create_pokerboard_without_title(self):
        """
        Create pokerboard without title.
        """
        data = {
            "description": "4th time",
        }
        response = self.client.post(self.POKERBOARD_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = {
            "title": [
                "This field is required."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_pokerboard_without_description(self):
        """
        Create pokerboard without description.
        """
        data = {
            "title": "4th time",
        }
        response = self.client.post(self.POKERBOARD_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = {
            "description": [
                "This field is required."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_pokerboard_details(self):
        """
        Test get pokerboard details
        """
        expected_data = {
            "id": self.pokerboard.id,
            "manager": self.pokerboard.manager.id,
            "title": self.pokerboard.title,
            "description": self.pokerboard.description,
            "configuration": self.pokerboard.configuration
        }
        response = self.client.get(
            reverse("pokerboard-detail", args=[self.pokerboard.id]))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)



class UserPokerboardTestCases(APITestCase):
    """
    Test case for user pokerboard API.
    """

    def setUp(self):
        """
        Setup method for creating user and its token.
        """
        self.user1 = G(User, email="tv114@gmail.com")
        self.user2 = G(User, email="ms114@gmail.com")
        self.token1 = G(Token, user=self.user1)
        self.token2 = G(Token, user=self.user2)
        self.pokerboard = G(Pokerboard, manager=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        self.group1 = G(Group, created_by=self.user1, name="mygroup")
        self.group1.users.add(self.user1)
        self.group1.users.add(self.user2)
        self.MEMBERS_URL = f"/pokerboard/{self.pokerboard.id}/members/"

    def test_delete_user_does_not_exist(self):
        """
        Delete user which does not exist.
        """
        data = {
            "email": "temp@gmail.com"
        }
        response = self.client.delete(self.MEMBERS_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = {
            "non_field_errors": [
                "Invalid email!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_delete_user_not_member_of_pokerboard(self):
        """
        Delete user which is not member of pokerboard
        """
        data = {
            "email": self.user2.email
        }
        response = self.client.delete(self.MEMBERS_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = {
            "non_field_errors": [
                "User not member of pokerboard!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_delete_group_not_part_of_pokerboard(self):
        """
        Delete group which is not part of pokerboard
        """
        data = {
            "group_id": self.group1.id
        }
        response = self.client.delete(self.MEMBERS_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = {
            "non_field_errors": [
                "No members found!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_delete_user_from_pokerboard(self):
        """
        Test case to delete user from pokerboard.
        """
        data = {
            "email": self.user2.email
        }
        response = self.client.post(
            f"/pokerboard/{self.pokerboard.id}/invite/", data=data)
        if response.status_code == 200:
            self.client.credentials(
                HTTP_AUTHORIZATION='Token ' + self.token2.key)
            response = self.client.patch(
                f"/pokerboard/{self.pokerboard.id}/invite/")
            if response.status_code == 200:
                data = {
                    "email": self.user2.email
                }
                self.client.credentials(
                    HTTP_AUTHORIZATION='Token ' + self.token1.key)
                response = self.client.delete(self.MEMBERS_URL, data=json.dumps(
                    data), content_type="application/json")
                expected_data = {
                    "msg": "Successfully removed from pokerboard"
                }
                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(expected_data, response.data)
