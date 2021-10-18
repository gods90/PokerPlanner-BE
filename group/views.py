from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from group.models import Group
from group.serializer.serializers import GroupSerializer, GroupUpdateSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group View for Performing CRUD operations.
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    
    def get_serializer_class(self, *args, **kwargs):
        method = self.request.method
        if method == 'PATCH':
            return GroupUpdateSerializer
        return super().get_serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={**request.data,'created_by':request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    

