from rest_framework import serializers

from group.models import Group
from user.models import User
from user.serializers import GetUserSerializer


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer to get group details : 
    name, members, created_by
    """
    users = GetUserSerializer(many=True, required=False)
    creator_email = serializers.CharField(read_only=True, source='created_by')

    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name', 'users', 'creator_email']

    def create(self, validated_data):
        """
        Creates group object with current user as admin
        and adds user in group as member.
        """
        name = validated_data["name"]
        user = validated_data["created_by"]
        group = Group.objects.create(name=name, created_by=user)
        group.users.add(user)
        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer to validate user which is to be added in the group.
    """
    email = serializers.EmailField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'email', 'first_name', 'last_name']

    def get_first_name(self, instance):
        """
        Return first_name of user most recently added
        """
        user = User.objects.get(email=instance.email)
        return user.first_name
    
    def get_last_name(self, instance):
        """
        Return last_name of user most recently added
        """
        user = User.objects.get(email=instance.email)
        return user.last_name

    def validate_email(self, attrs):
        """
        To validate email, user exists and not already in group.
        """
        user = User.objects.filter(email=attrs)
        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
        else:
            if self.instance.users.filter(email=attrs).exists():
                raise serializers.ValidationError('Already a member!')
        self.context['user'] = user.first()
        return attrs

    def update(self, instance, validated_data):
        """
        Add user in the group.
        """
        if 'email' not in validated_data:
            raise serializers.ValidationError("Email is required.")
        user = self.context['user']
        instance.users.add(user)
        return super().update(instance, validated_data)


class GroupMemberDeleteSerializer(serializers.Serializer):
    """
    Serializer to remove user from a group.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_user(self, user):
        """
        Validating user which is to be removed.
        """
        group = self.context['group']
        if group.created_by == user:
            raise serializers.ValidationError(
                "Cannot delete creator of group."
            )
        return user


class GetGroupSerializer(serializers.ModelSerializer):
    """
    Serializer to get group.
    """
    class Meta:
        model = Group
        fields = ['name','id']


class GroupFindSerializer(serializers.ModelSerializer):
    """
    Serializer to return group to add to the pokerboard
    """
    created_by_email = serializers.EmailField(source='created_by')
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'created_by_email']
