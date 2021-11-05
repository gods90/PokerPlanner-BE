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

    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name', 'users']

    def to_representation(self, instance):
        """
        Replacing group_admin_id with his/her fullname.
        """
        repr = super().to_representation(instance)
        repr["creator_name"] = f"{instance.created_by.first_name} {instance.created_by.last_name}"
        return repr

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

    class Meta:
        model = Group
        fields = ['id', 'name', 'email']

    def to_representation(self, instance):
        """
        Adding fullname of user recently added.
        """
        repr = super().to_representation(instance)
        user = User.objects.get(email=instance.email)
        repr["first_name"] = user.first_name
        repr["last_name"] = user.last_name
        return repr

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
        return super().validate(attrs)

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

        group = Group.objects.get(id=self.context['group_id'])
        if group.created_by == user[0]:
            raise serializers.ValidationError(
                "Cannot delete creator of group."
            )
        if not group.users.filter(email=attrs).exists():
            raise serializers.ValidationError('User not part of group.')


class GetGroupSerializer(serializers.ModelSerializer):
    """
    Serializer to get group.
    """
    class Meta:
        model = Group
        fields = ["name"]
