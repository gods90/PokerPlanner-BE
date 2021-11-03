import json
from ddf import G

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from group.models import Group
from invite.models import Invite
from pokerboard import constants
from user.models import User
from pokerboard.models import Pokerboard


class InviteTestCases(APITestCase):
    """
    Test case for invite to pokerboard API
    """
    def setUp(self):
        """
        Setup method for creating user,token and group.
        """
        self.user1 = G(User, email="tv114@gmail.com")
        self.user2 = G(User, email="ms114@gmail.com")
        self.user3 = G(User, email="ym114@gmail.com")
        self.token1 = G(Token, user=self.user1)
        self.pokerboard = G(Pokerboard, manager=self.user1, game_duration="30")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        self.group1 = G(Group, created_by=self.user3, name="mygroup")
        self.group1.users.add(self.user3)

        self.group2 = G(Group, created_by=self.user2, name="mygroup")
        self.group2.users.add(self.user2)
        self.group2.users.add(self.user3)
        self.INVITE_URL = reverse('invite-list')

    def test_invite_user(self):
        """
        Invites user testcases
        """
        data = {
            "email": self.user2.email,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)

        expected_data = {
            "pokerboard": self.pokerboard.id,
            "group_id": None,
            "user_role": constants.PLAYER
        }
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(expected_data, response.data)

        # Invites user by passing user email who is already invited.
        data = {
            "email": self.user2.email,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Invite already sent!"
        ]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

        # #Accepting invite
        invite = Invite.objects.get(
            pokerboard_id=self.pokerboard.id, user_id=self.user2)
        self.INVITE_URL_DETAIL = reverse('invite-detail', args=[invite.id])
        token2 = G(Token, user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.patch(self.INVITE_URL_DETAIL, data={})
        expected_data = {
            'group': None,
            'id': invite.id,
            'pokerboard': self.pokerboard.id,
            'pokerboard_title': self.pokerboard.title,
            'status': "ACCEPTED",
            'user': self.user2.id,
            'user_role': constants.ROLE_CHOICES[invite.user_role][1]
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)

        # #Inviting user when invite is already accepted.
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Already part of pokerboard"
        ]
        self.assertListEqual(expected_data, response.data)
        self.assertEqual(response.status_code, 400)

        # #Deleting invite when alredy accepted.
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        invite = Invite.objects.get(user=self.user2)
        response = self.client.delete(
            reverse('invite-detail', args=[invite.id]))
        expected_data = {
            "detail": "Not found."
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)

    def test_invite_user_passing_manager_email(self):
        """
        Invites user by passing manager email.
        """
        data = {
            "pokerboard": self.pokerboard,
            "email": self.user1.email
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Manager cannot be invited!"
        ]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

    def test_invite_not_signed_user(self):
        """
        Invites user who has not signed.
        """
        data = {
            "email": "yogendra.manral@joshtechnologygroup.com",
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Email to signup in pokerplanner has been sent.Please check your email."
        ]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

    def test_invite_by_group(self):
        """
        Invite by group id.
        """
        data = {
            "group_id": self.group2.id,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = {
            "pokerboard": self.pokerboard.id,
            "group_id": self.group2.id,
            "user_role": constants.PLAYER
        }
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(expected_data, response.data)

        # Sending invite if one person is in 2 group.
        data = {
            "group_id": self.group1.id,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Invite already sent!"
        ]
        self.assertListEqual(expected_data, response.data)
        self.assertEqual(response.status_code, 400)

    def test_invite_without_passing_email_or_groupid(self):
        """
        Invite user without passing email or group id.
        """
        data = {
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Provide group_id/email!"
        ]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

    def test_invite_without_passing_pokerboard(self):
        """
        Invite user without passing email or group id.
        """
        data = {
            "email": self.user2.email
        }
        response = self.client.post(self.INVITE_URL, data=json.dumps(
            data), content_type='application/json')
        expected_data = {
            "pokerboard": ["This field is required."]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_invite_user_by_not_manager(self):
        """
        Testcase to invite user by not manager.
        """
        data = {
            "email": self.user2.email,
            "pokerboard": self.pokerboard.id
        }
        token2 = G(Token, user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.post(self.INVITE_URL, data=data)
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
            "email": self.user3.email,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        if self.assertEqual(response.status_code, 201):
            invite = Invite.objects.get(
                email=data['email'], pokerboard=data['pokerboard'])
            response = self.client.delete(
                reverse('invite-detail', args=[invite.id]))
            expected_data = {
                "msg": "Invite successfully revoked."
            }
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(expected_data, response.data)

    def test_delete_invite_not_exist(self):
        """
        Test case to delete invite which does not exist.
        """
        response = self.client.delete(reverse('invite-detail', args=[500]))
        expected_data = {
            "detail": "Not found."
        }
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)
