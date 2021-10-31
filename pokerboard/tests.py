import json
from os import posix_fallocate

from ddf import G
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from group.models import Group
from pokerboard.admin import PokerboardAdmin
from pokerboard.models import Pokerboard
from user.models import User


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
        self.pokerboard = G(Pokerboard, manager=self.user,game_duration="30")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_pokerboard(self):
        """
        Create pokerboard give title and description
        """
        data = {
            'title': 'csk',
            'description': '4th time',
            "configuration": 3,
            "game_duration":"30",
            "tickets":["PP-1"]
        }
        response = self.client.post(self.POKERBOARD_URL, data=json.dumps(
            data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        pokerboard = Pokerboard.objects.get(id=response.data["id"])

        seconds = pokerboard.game_duration.seconds
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        
        expected_data = {
            "id": pokerboard.id,
            "manager": pokerboard.manager.id,
            "title": pokerboard.title,
            "description": pokerboard.description,
            "game_duration":'{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
            'ticket_responses':[{
                'estimate': None,
                'status_code': 200,
                'key': 'PP-1'
            }]
        }
        self.assertEqual(response.status_code,201)
        self.assertDictEqual(expected_data, response.data)

    def test_create_pokerboard_without_title(self):
        """
        Create pokerboard without title.
        """
        data = {
            "description": "4th time",
            "game_duration":"30"
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
            "game_duration":"30"
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

    def test_create_pokerboard_without_game_duration(self):
        """
        Create pokerboard without description.
        """
        data = {
            "title": "4th time",
            "description":"desc",
        }
        response = self.client.post(self.POKERBOARD_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = {
            "game_duration": [
                "This field is required."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_pokerboard_without_tickets(self):
        """
        Create pokerboard without description.
        """
        data = {
            "title": "4th time",
            "description": "desc",
            "game_duration":"30"
        }
        response = self.client.post(self.POKERBOARD_URL, data=json.dumps(
            data), content_type="application/json")
        expected_data = [
                "Invalid Query"
        ]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

    def test_pokerboard_details(self):
        """
        Test get pokerboard details
        """

        pokerboard = Pokerboard.objects.get(id=self.pokerboard.id)

        seconds = pokerboard.game_duration.seconds
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60

        expected_data = {
            "id": self.pokerboard.id,
            "manager": self.pokerboard.manager.id,
            "title": self.pokerboard.title,
            "description": self.pokerboard.description,
            "game_duration":'{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
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
        self.pokerboard = G(Pokerboard, manager=self.user1, game_duration="30")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        self.group1 = G(Group, created_by=self.user1, name="mygroup")
        self.group1.users.add(self.user1)
        self.group1.users.add(self.user2)
        self.MEMBERS_URL = f"/pokerboard/{self.pokerboard.id}/members/"

    def test_delete_user_does_not_exist_in_pokerboard(self):
        """
        Delete user which does not exist in pokerboard.
        """
        response = self.client.delete(reverse("members-detail",args=[self.pokerboard.id,5]))
        expected_data = {
            "detail": 
                "Not found."
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)

    def test_delete_group_not_part_of_pokerboard(self):
        """
        Delete group which is not part of pokerboard
        """
        response = self.client.delete(reverse("groups-detail",args=[self.pokerboard.id,12]))
        expected_data = {
            "detail": 
                "Not found."
            
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)

    def test_delete_user_from_pokerboard(self):
        """
        Test case to delete user from pokerboard.
        """
        data = {
            "email": self.user2.email
        }
        response = self.client.post(reverse('members-list',args=[self.pokerboard.id]), data=data)
        if response.status_code == 200:
            self.client.credentials(
                HTTP_AUTHORIZATION='Token ' + self.token2.key)
            response = self.client.patch(reverse('members-list',args=[self.pokerboard.id]))
            if response.status_code == 200:
                self.client.credentials(
                    HTTP_AUTHORIZATION='Token ' + self.token1.key)
                response = self.client.delete(reverse('members-detail',args=[self.pokerboard.id,self.user2.id]))
                expected_data = {
                    "msg": "Successfully removed from pokerboard"
                }
                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(expected_data, response.data)
