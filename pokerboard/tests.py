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
        self.user = G(User,email="tv114@gmail.com")
        token = G(Token, user = self.user)
        self.pokerboard = G(Pokerboard,manager=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    
    def test_create_pokerboard(self):
        """
        Create pokerboard give title and description
        """
        data = {
            'title': 'csk',
            'description':'4th time',
            "configuration":3
        }
        response = self.client.post(self.POKERBOARD_URL,data=json.dumps(data),content_type="application/json")
        
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
            "description":"4th time",
        }
        response = self.client.post(self.POKERBOARD_URL,data=json.dumps(data),content_type="application/json")
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
            "title":"4th time",
        }
        response = self.client.post(self.POKERBOARD_URL,data=json.dumps(data),content_type="application/json")
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
            "configuration":self.pokerboard.configuration
        }
        response = self.client.get(reverse("pokerboard-detail", args=[self.pokerboard.id]))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)
    
    
class InviteTestCases(APITestCase):
    """
    Test case for invite to pokerboard API
    """
    def setUp(self):
        """
        Setup method for creating user,token and group.
        """
        self.user1 = G(User,email="tv114@gmail.com")
        self.user2 = G(User,email="ms114@gmail.com")
        self.user3 = G(User,email="ym114@gmail.com")
        self.token1 = G(Token, user = self.user1)
        self.pokerboard = G(Pokerboard,manager=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        self.group1 = G(Group, created_by=self.user1,name = "mygroup")
        self.group1.users.add(self.user1)
        self.group1.users.add(self.user2)
        
        self.group2 = G(Group, created_by=self.user1,name = "mygroup")
        self.group2.users.add(self.user1)
        self.group2.users.add(self.user2)
        self.group2.users.add(self.user3)
        self.INVITE_URL = f"/pokerboard/{self.pokerboard.id}/invite/"
        
    def test_invite_user(self):
        """
        Invites user testcases
        """
        data = {
            "email": self.user2.email
        }
        response = self.client.post(self.INVITE_URL,data=data)
        expected_data = {
            "msg": "User successfully invited"
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)
        
        #Checking if invite is not created for manager
        response = self.client.patch(self.INVITE_URL,data={})
        expected_data = {
            "non_field_errors": [
                "Invite doesnt exists"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
        #Invites user by passing user email who is already invited.
        data = {
            "email": self.user2.email
        }
        response = self.client.post(self.INVITE_URL,data=data)
        expected_data = {
            "non_field_errors": [
                "Invite already sent!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
        #Accepting invite
        token2 = G(Token, user = self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.patch(self.INVITE_URL,data={})
        expected_data = {
            "msg": "Welcome to the pokerboard!"
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)
        
        #Inviting user when invite is already accepted by post or patch request.
        response = self.client.patch(self.INVITE_URL,data=data)
        expected_data = {
            "non_field_errors": [
                    "Already part of pokerboard."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
        #Deleting invite when alredy accepted.
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        data = {
            "email": self.user2.email
        }
        response = self.client.delete(self.INVITE_URL,data=data)
        expected_data = {
            "non_field_errors": [
                "Accepted invites cannot be revoked."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
        # Update role when role field not provided
        response = self.client.patch(f"/pokerboard/{self.pokerboard.id}/members/",data=json.dumps(data),
                                     content_type="application/json")
        expected_data = {
            "non_field_errors": [
                "Role not provided!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
    def test_invite_user_passing_manager_email(self):
        """
        Invites user by passing manager email.
        """
        data = {
            "email": self.user1.email
        }
        response = self.client.post(self.INVITE_URL,data=data)
        expected_data = {
            "non_field_errors": [
                "Manager cannot be invited!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
    # def test_invite_not_signed_user(self):
    #     """
    #     Invites user who has not signed.
    #     """
    #     data = {
    #         "email": "yogendra.manral@joshtechnologygroup.com"
    #     }
    #     response = self.client.post(self.INVITE_URL,data=data)
    #     expected_data = {
    #         "non_field_errors": [
    #             "Email to signup in pokerplanner has been sent.Please check your email."
    #         ]
    #     }
    #     self.assertEqual(response.status_code, 400)
    #     self.assertDictEqual(expected_data, response.data)
    
    def test_invite_by_group(self):
        """
        Invite by group id.
        """
        data = {
            "group_id": self.group1.id
        }
        response = self.client.post(self.INVITE_URL,data=data)
        expected_data = {
            "msg": "Group successfully invited"
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)
    
        # Sending invite if one person is in 2 group.
        data = {
            "group_id": self.group2.id
        }
        response = self.client.post(self.INVITE_URL,data=data)
        expected_data = {
            "non_field_errors": [
                "Invite already sent!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
        
    def test_invite_without_passing_email_or_groupid(self):
        """
        Invite user without passing email or group id.
        """
        response = self.client.post(self.INVITE_URL,data={})
        expected_data = {
            "non_field_errors": [
                "Provide group_id/email!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
   
    def test_invite_user_by_not_manager(self):
        """
        Testcase to invite user by not manager.
        """ 
        data = {
            "email": self.user2.email
        }
        token2 = G(Token, user = self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.post(self.INVITE_URL,data=data)
        expected_data = {
            "detail": "You do not have permission to perform this action."
        }
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(expected_data, response.data)
    
    def test_delete_invite(self):
        """
        Test case to delete invite.
        """
        data = {
            "email": self.user3.email
        }
        response = self.client.post(self.INVITE_URL,data=data)
        if self.assertEqual(response.status_code, 200):
            response = self.client.delete(self.INVITE_URL,data=data)
            expected_data = {
                "msg": "Invite successfully revoked."
            }
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(expected_data, response.data)
    
    def test_delete_invite_not_exist(self):
        """
        Test case to delete invite which does not exist.
        """
        data = {
            "email": self.user3.email
        }
        response = self.client.delete(self.INVITE_URL,data=data)
        expected_data = {
            "non_field_errors": [
                "User not invited!"
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
    

class UserPokerboardTestCases(APITestCase):
    """
    Test case for user pokerboard API.
    """
    def setUp(self):
        """
        Setup method for creating user and its token.
        """
        self.user1 = G(User,email="tv114@gmail.com")
        self.user2 = G(User,email="ms114@gmail.com")
        self.token1 = G(Token, user = self.user1)
        self.token2 = G(Token, user = self.user2)
        self.pokerboard = G(Pokerboard,manager=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        self.group1 = G(Group, created_by=self.user1,name = "mygroup")
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
        response = self.client.delete(self.MEMBERS_URL,data=json.dumps(data),content_type="application/json")
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
        response = self.client.delete(self.MEMBERS_URL,data=json.dumps(data),content_type="application/json")
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
        response = self.client.delete(self.MEMBERS_URL,data=json.dumps(data),content_type="application/json")
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
            "email":self.user2.email
        }
        response = self.client.post(f"/pokerboard/{self.pokerboard.id}/invite/",data=data)
        if response.status_code == 200:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
            response = self.client.patch(f"/pokerboard/{self.pokerboard.id}/invite/")
            if response.status_code == 200:
                data = {
                    "email": self.user2.email
                }
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
                response = self.client.delete(self.MEMBERS_URL,data=json.dumps(data),content_type="application/json")
                expected_data = {
                    "msg": "Successfully removed from pokerboard"
                }
                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(expected_data, response.data)