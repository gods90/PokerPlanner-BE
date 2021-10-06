from ddf import G

from rest_framework.test import APITestCase

from django.urls import reverse

from user import models


class TestCases(APITestCase):
    REGISTER_URL = reverse('user-list')
    LOGIN_URL = reverse('login')

    def setUp(self):
        """
        Setup method for creating default user and it's token
        """
        self.user = G(models.User)

    def test_create_user(self):
        """
        Test create user
        """
        data = {
            "first_name": "Nick",
            "last_name": "Jonas",
            "email": "nick.jonas@joshtechnologygroup.com",
            "password": "Password@123",
        }
        response = self.client.post(self.REGISTER_URL, data=data)
        response.data.pop("id")
        self.assertEqual(response.status_code, 201)
        user = models.User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
        expected_data = {
            "username":"",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
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
        response.data.pop("id")
        self.assertEqual(response.status_code, 201)
        user = models.User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
        expected_data = {
            "username":"",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
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
        Test create user with invalid password
        """
        self.test_create_user()
        data = {
            "first_name": "Anshul",
            "last_name": "Garg",
            "email": "nick.jonas@joshtechnologygroup.com",
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
        
    def test_login(self):
        self.test_create_user()
        data = {
            "email": "nick.jonas@joshtechnologygroup.com",
            "password": "Password@123",
        }
        response = self.client.post(self.LOGIN_URL, data=data)
        self.assertEqual(response.status_code, 200)
        user = models.User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
    
    def test_login_invalid_password(self):
        self.test_create_user()
        data = {
            "email": "nick.jonas@joshtechnologygroup.com",
            "password": "Password123",
        }
        response = self.client.post(self.LOGIN_URL, data=data)
        expected_data = {
            "error": "Invalid Credentials"
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
    
    def test_login_invalid_email(self):
        self.test_create_user()
        data = {
            "email": "nick.jone@joshtechnologygroup.com",
            "password": "Password@123",
        }
        response = self.client.post(self.LOGIN_URL, data=data)
        expected_data = {
            "error": "Invalid Credentials"
        }
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)
            