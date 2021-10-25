from ddf import G
import json

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.urls import reverse

from group.models import Group
from user.models import User


class GroupTestCases(APITestCase):
    """
    Group testcases for testing group list, details and add member functionality
    """
    GROUP_URL = reverse('group-list')

    def setUp(self):
        """
        Setup method for creating default user and it's token
        """
        self.user1 = G(User, email="temp1@gmail.com")
        token = G(Token, user=self.user1)
        self.group = G(Group, created_by=self.user1, name="mygroup")
        self.group.users.add(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_group(self):
        """
        Test case to create group with default user as logged in user.
        """
        data = {
            'name': 'csk'
        }
        response = self.client.post(self.GROUP_URL, data=json.dumps(
            data), content_type="application/json")
        group = Group.objects.get(name="csk")
        expected_data = {
            "id": group.id,
            "name": group.name,
            "created_by": group.created_by.id,
            "users": [
                {
                    "id": self.user1.id,
                    "email": self.user1.email,
                    "first_name": self.user1.first_name,
                    "last_name": self.user1.last_name,
                }
            ],
            "creator_name": f"{self.user1.first_name} {self.user1.last_name}"
        }
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(expected_data, response.data)

    def test_create_group_with_empty_name(self):
        """
        On empty group name shows bad request.
        """
        data = {
            "name": ""
        }
        expected_data = {
            "name": [
                "This field may not be blank."
            ]
        }
        response = self.client.post(self.GROUP_URL, data=json.dumps(
            data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_create_group_without_passing_name(self):
        """
        On not passing group field bad request is received
        """
        data = {}
        expected_data = {
            "name": [
                "This field is required."
            ]
        }
        response = self.client.post(self.GROUP_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_to_group(self):
        """
        Add member to group, Expects 200 response code
        """
        user2 = G(User, email="temp2@gmail.com")
        data = {
            "email": user2.email
        }
        response = self.client.patch(
            reverse('group-detail', args=[self.group.id]), data=data)
        self.assertEqual(response.status_code, 200)

        # Get group list.Here users will be creator of group and the above added user.
        response = self.client.get(self.GROUP_URL)
        group = Group.objects.get(name=self.group.name)
        user1 = User.objects.get(id=group.created_by_id)

        # deleting keys by pagination
        del response.data["count"]
        del response.data["previous"]
        del response.data["next"]

        expected_data = {
            "results": [
                {
                    "id": group.id,
                    "name": group.name,
                    "created_by": group.created_by.id,
                    "users": [
                        {
                            "email": user1.email,
                            "first_name": user1.first_name,
                            "last_name": user1.last_name,
                            "id": user1.id
                        },
                        {
                            "email": user2.email,
                            "first_name": user2.first_name,
                            "last_name": user2.last_name,
                            "id": user2.id
                        }
                    ],
                    "creator_name": f"{self.user1.first_name} {self.user1.last_name}"
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)

        # Expects 400 response code on adding a member more than one time
        data = {
            "email": user2.email
        }
        expected_data = {
            "email": [
                "Already a member!"
            ]
        }
        response = self.client.patch(
            reverse('group-detail', args=[self.group.id]), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_not_existing(self):
        """
        Expects 400 response code on adding a not existing member.
        """
        data = {
            "email": "notexisting@gmail.com"
        }
        expected_data = {
            "email": [
                "Invalid user!"
            ]
        }
        response = self.client.patch(
            reverse('group-detail', args=[self.group.id]), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_group_does_not_exist(self):
        """
        Expects 400 response code on adding a member to not existing group.
        """
        data = {
            "email": "temp1@gmail.com"
        }
        expected_data = {
            "detail": "Not found."
        }
        response = self.client.patch(
            reverse('group-detail', args=[500]), data=data)
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_without_passing_email(self):
        """
        Expects 400 response code without passing email field.
        """
        expected_data = [
            "This field is required."
        ]
        response = self.client.patch(
            reverse('group-detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(response.data, expected_data)

    def test_add_member_by_not_creator(self):
        """
        Add member to group by not creator of group, Expects 403 response code
        """
        user2 = G(User, email="temp2@gmail.com")
        data = {
            "email": user2.email
        }
        expected_data = {
            "detail": "You do not have permission to perform this action."
        }
        token2 = G(Token, user=user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.patch(
            reverse('group-detail', args=[self.group.id]), data=data)
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(expected_data, response.data)

    def test_get_group_by_id(self):
        """
        Get group detail by giving its id.
        """
        response = self.client.get(
            reverse('group-detail', args=[self.group.id]))
        group = Group.objects.get(name=self.group.name)
        user = User.objects.get(id=group.created_by_id)
        expected_data = {
            "id": group.id,
            "created_by": group.created_by.id,
            "name": group.name,
            "users": [
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "id": user.id
                }
            ],
            "creator_name": f"{self.user1.first_name} {self.user1.last_name}"
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)

    def test_get_group_by_id_not_found(self):
        """
        If id does not exist shows detail not found.
        """
        response = self.client.get(reverse('group-detail', args=[500]))
        expected_data = {
            "detail": "Not found."
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)

    def test_delete_group_(self):
        """
        Test case to delete group.
        """
        response = self.client.delete(
            reverse('group-detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 204)
        # 0 groups exist after deletion
        self.assertEqual(len(Group.objects.filter(id=self.group.id)), 0)

    def test_delete_group_does_not_exist(self):
        """
        Test case to delete group which does not exist.
        """
        response = self.client.delete(reverse('group-detail', args=[500]))
        expected_data = {
            "detail": "Not found."
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)
