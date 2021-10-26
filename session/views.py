from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from session.models import Session
from session.serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    Session View for CRUD operations
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
            Create new session
            Required : Token in header, Title, tickets/sprint/jql(atleast one)
        """
        serializer = self.get_serializer(data = {**request.data})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
