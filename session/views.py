from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from session.models import Session
from session.serializers import SessionSerializer, SessionCreateSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    Session View for CRUD operations
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        # import pdb
        # pdb.set_trace()
        if(self.request.method == 'POST'):
            return SessionCreateSerializer
        return super().get_serializer(*args, **kwargs)

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
