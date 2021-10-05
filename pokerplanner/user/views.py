from django.contrib.auth import authenticate

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework import viewsets

from pokerplanner.user.models import User
from pokerplanner.user.serializers import UserSerializer
from pokerplanner.user.serializers import UserSerializerToken


class UserViewSet(viewsets.ModelViewSet):
    """
    User View for Performing CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomAuthToken(ObtainAuthToken):
    """
    Class to generate token.
    """

    def post(self, request, *args, **kwargs):
        serializer = UserSerializerToken(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)
        if user is None:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key
        }, status=status.HTTP_200_OK)
