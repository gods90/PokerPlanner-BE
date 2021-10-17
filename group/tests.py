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
        self.user = G(User,email="tv114@gmail.com")
        token = G(Token, user = self.user)
        self.group = G(Group, created_by=self.user,name = "mygroup")
        self.group.users.add(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_group(self):
        """
        Test case to create group with default user as logged in user.
        """
        data = {
            'name': 'csk'
        }
        group = Group.objects.get(name = "mygroup")
        group.delete()
        response = self.client.post(self.GROUP_URL, data=data)
        group = Group.objects.get(name="csk")
        expected_data = {
            "id": group.id,
            "name": group.name,
            "created_by": group.created_by.id,
            "users": [
                {
                    "email": self.user.email,
                }
            ]
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
                "This field cannot be blank."
            ]
        }
        group = Group.objects.get(name = "mygroup")
        group.delete()
        response = self.client.post(self.GROUP_URL, data=data)
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
    
    def test_list_group(self):
        """
        Get group list default user will be the creator of the group.
        """
        response = self.client.get(self.GROUP_URL)
        group = Group.objects.get(name=self.group.name)
        user = User.objects.get(id=group.created_by_id)
        expected_data = [
            {
                "id": group.id,
                "name": group.name,
                "created_by": group.created_by.id,
                "users": [
                    {
                        "email": user.email
                    }
                ]
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(expected_data, response.data)
    
    def test_get_group_by_id(self):
        """
        Get group detail by giving its id.
        """
        response = self.client.get(reverse('group-detail',args=[self.group.id]))
        group = Group.objects.get(name=self.group.name)
        user = User.objects.get(id=group.created_by_id)
        expected_data = {
                "id": group.id,
                "created_by": group.created_by.id,
                "name": group.name,
                "users": [
                    {
                        "email": user.email
                    }
                ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)
        
    def test_get_group_by_id_not_found(self):
        """
        If id does not exist shows detail not found.
        """
        response = self.client.get(reverse('group-detail',args=[500]))
        expected_data = {
            "detail": "Not found."
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)
    
    def test_add_member_to_group(self):
        """
        Add member to group, Expects 201 response code
        """
        user = G(User,email="temp1@gmail.com")
        data = {
            "email": user.email
        }
        response = self.client.patch(reverse('group-detail',args=[self.group.id]),data=data)
        group = Group.objects.get(name=self.group.name)   
        expected_data = {
            "id": group.id,
            "created_by": group.created_by.id,
            "name": group.name,
            "email": user.email
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_data)
    
    def test_add_member_morethan_once(self):
        """
        Expects 400 response code on adding a member more than one time
        """
        data = {
            "email": self.user.email
        }
        expected_data = {
            "email": [
                "Already a member!"
            ]
        }
        response = self.client.patch(reverse('group-detail',args=[self.group.id]),data=data)
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
        response = self.client.patch(reverse('group-detail',args=[self.group.id]),data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)
    
    def test_add_member_without_passing_email(self):
        """
        Expects 400 response code without passing email field.
        """
        expected_data = [
            "This field is required."
        ]
        response = self.client.patch(reverse('group-detail',args=[self.group.id]))
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(response.data, expected_data)


