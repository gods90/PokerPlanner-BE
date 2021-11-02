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
    name = serializers.CharField()
    creater_name = serializers.CharField(
        read_only=True, source='created_by.full_name'
    )

    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name', 'users', 'creater_name']

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
        return attrs

    def update(self, instance, validated_data):
        """
        Add user in the group.
        """
        if 'email' not in validated_data:
            raise serializers.ValidationError("Email is required.")
        user = User.objects.get(email=validated_data['email'])
        instance.users.add(user)
        return super().update(instance, validated_data)


class GroupMemberDeleteSerializer(serializers.Serializer):
    """
    Serializer to remove user from a group.
    """
    email = serializers.EmailField()

    def validate_email(self, attrs):
        """
        Validating email of user which is to be removed.
        """
        user = User.objects.filter(email=attrs)
        if not user.exists():
            raise serializers.ValidationError('Invalid user!')

        group = self.context['group_id']
        if group.created_by == user[0]:
            raise serializers.ValidationError(
                "Cannot delete creator of group."
            )
        if not group.users.filter(email=attrs).exists():
            raise serializers.ValidationError('User not part of group.')
        return attrs


class GetGroupSerializer(serializers.ModelSerializer):
    """
    Serializer to get group.
    """
    class Meta:
        model = Group
        fields = ["name"]
