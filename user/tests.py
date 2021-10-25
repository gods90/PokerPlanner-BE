from ddf import G

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.urls import reverse

from user.models import User


class CreateUserTest(APITestCase):
    REGISTER_URL = reverse('user')

    def setUp(self):
        """
        Setup method for creating default user.
        """
        self.user = G(User, email="tv114@gmail.com")

    def test_create_user(self):
        """
        Test create user
        """
        # Creating new user.
        data = {
            "username": "",
            "first_name": "Nick",
            "last_name": "Jonas",
            "email": "nick.jonas@joshtechnologygroup.com",
            "password": "Password@123",
        }

        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 201)
        user = User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
        expected_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "group": []
        }
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_without_first_name(self):
        """
        Test create user without first_name
        """
        data = {
            "last_name": "Jonas",
            "email": "nick.jonas@joshtechnologygroup.com",
            "password": "Password@123",
        }
        expected_data = {
            "first_name": [
                "This field is required."
            ]
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_without_last_name(self):
        """
        Test create user without last_name
        """
        data = {
            "first_name": "nick",
            "email": "nick.jonas@joshtechnologygroup.com",
            "password": "Password@123",
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 201)
        user = User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
        expected_data = {
            "id": user.id,
            "username": "",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "group": []
        }
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_without_email(self):
        """
        Test create user without email
        """
        data = {
            "first_name": "Nick",
            "last_name": "Jonas",
            "password": "Password@123",
        }
        expected_data = {
            "email": [
                "This field is required."
            ]
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_with_invalid_email(self):
        """
        Test create user with invalid email
        """
        data = {
            "first_name": "Nick",
            "last_name": "Jonas",
            "email": "nick123gmail.com",
            "password": "Password@123",
        }
        expected_data = {
            "email": [
                "Enter a valid email address."
            ]
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_without_password(self):
        """
        Test create user without password
        """
        data = {
            "first_name": "Nick",
            "last_name": "Jonas",
            "email": "nick.jonas@joshtechnologygroup.com",
        }
        expected_data = {
            "password": [
                "This field is required."
            ]
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_with_invalid_password(self):
        """
        Test create user with invalid password
        """
        data = {
            "first_name": "Nick",
            "last_name": "Jonas",
            "email": "nick@123gmail.com",
            "password": "Password123",
        }
        expected_data = {
            "password": [
                "Password should be atleast of length 8,one number must contain one uppercase, one lowercase one special character!"
            ]
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_create_user_with_existing_email(self):
        """
        Test create user with existing email.
        """
        data = {
            "first_name": "Anshul",
            "last_name": "Garg",
            "email": self.user.email,
            "password": "Password@123",
        }
        expected_data = {
            "email": [
                "user with this email already exists."
            ]
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)


class UpdateTestCases(APITestCase):
    UPDATE_URL = reverse('user')

    def setUp(self):
        """
        Setup method for creating default user.
        """
        self.user = G(User, email="temp1@gmail.com", first_name="temp1")
        token = G(Token, user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_update_user_first_name(self):
        """
        Test update user first name
        """
        data = {
            "first_name": "Tushar",
        }
        response = self.client.patch(self.UPDATE_URL, data=data)
        user = User.objects.get(email=self.user.email)
        expected_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "group": []
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)

    def test_update_user_last_name(self):
        """
        Test update user last name
        """
        data = {
            "last_name": "Gupta",
        }
        response = self.client.patch(self.UPDATE_URL, data=data)
        user = User.objects.get(email=self.user.email)
        expected_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "group": []
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)

    def test_update_user_password(self):
        """
        Test update user password
        """
        data = {
            "password": "Tushar@1170",
        }
        response = self.client.patch(self.UPDATE_URL, data=data)
        user = User.objects.get(email=self.user.email)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.password, data["password"])

    def test_update_user_invalid_password(self):
        """
        Test update user with invalid password
        """
        data = {
            "password": "Tushar",
        }
        expected_data = {
            "password": [
                "Password should be atleast of length 8,one number must contain one uppercase, one lowercase one special character!"
            ]
        }
        response = self.client.patch(self.UPDATE_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)


class GetTestCases(APITestCase):
    GET_URL = reverse('user')

    def setUp(self):
        """
        Setup method for creating default user.
        """
        self.user = G(User)
        token = G(Token, user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_user(self):
        """
        Test to get user
        """
        user = User.objects.get(email=self.user.email)
        expected_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "group": []
        }
        response = self.client.get(self.GET_URL)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)


class DeleteTestCases(APITestCase):
    DELETE_URL = reverse('user')

    def setUp(self):
        """
        Setup method for creating default user.
        """
        self.user = G(User, email="temp1@gmail.com")
        token = G(Token, user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_delete_user(self):
        """
        Test to delete user
        """
        response = self.client.delete(self.DELETE_URL)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(User.objects.filter(email=self.user.email)), 0)


class LoginTestCases(APITestCase):
    LOGIN_URL = reverse('login')

    def setUp(self):
        """
        Setup method for creating default user.
        """
        self.user = G(User, email="tv114@gmail.com", password="tushar@1170",
                      first_name="tushar", username="tushar114")
        self.user.set_password(self.user.password)
        self.user.save()

    def test_login(self):
        data = {
            "username": self.user.email,
            "password": "tushar@1170"
        }
        user = User.objects.filter(email=data["username"]).first()
        response = self.client.post(self.LOGIN_URL, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(user)

    def test_login_invalid_password(self):
        data = {
            "username": "tv114@gmail.com",
            "password": "Password123",
        }
        response = self.client.post(self.LOGIN_URL, data=data)
        expected_data = {
            "non_field_errors": [
                "Unable to log in with provided credentials."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def test_login_invalid_email(self):
        data = {
            "username": "nick.jone@joshtechnologygroup.com",
            "password": "Password@123",
        }
        response = self.client.post(self.LOGIN_URL, data=data)
        expected_data = {
            "non_field_errors": [
                "Unable to log in with provided credentials."
            ]
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
