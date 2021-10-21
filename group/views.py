from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from group.models import Group
from group.permissions import CustomPermissions
from group.serializer.serializers import GroupSerializer, GroupUpdateSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group View for Performing CRUD operations.
    """
    
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated,CustomPermissions]
    
    
    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH']:
            return GroupUpdateSerializer
        return super().get_serializer_class()


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={**request.data,'created_by':request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Group.objects.filter(users=self.request.user)

