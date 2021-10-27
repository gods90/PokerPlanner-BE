from rest_framework import serializers

from group.models import Group
from user.models import User
from user.serializer.serializers2 import GetUserSerializer


class GroupSerializer(serializers.ModelSerializer):
    users = GetUserSerializer(many=True, required=False)
    name = serializers.CharField()

    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name', 'users']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["creator_name"] = f"{instance.created_by.first_name} {instance.created_by.last_name}"
        return repr

    def create(self, validated_data):
        """
        Creates group object with default user as admin
        """
        name = validated_data["name"]
        user = validated_data["created_by"]
        group = Group.objects.create(name=name, created_by=user)
        group.users.add(user)
        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    created_by = serializers.PrimaryKeyRelatedField(
        required=False, read_only=True)
    name = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'created_by', 'name', 'email']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        user = User.objects.get(email=instance.email)
        repr["first_name"] = user.first_name
        repr["last_name"] = user.last_name
        return repr

    def validate_email(self, attrs):
        user = User.objects.filter(email=attrs)
        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
        else:
            if self.instance.users.filter(email=attrs).exists():
                raise serializers.ValidationError('Already a member!')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if 'email' not in validated_data:
            raise serializers.ValidationError("This field is required.")
        user = User.objects.get(email=validated_data['email'])
        instance.users.add(user)
        return super().update(instance, validated_data)


class GroupDeleteSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, attrs):
        user = User.objects.filter(email=attrs)
        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
        group = Group.objects.get(id=self.context['group_id'])
        if group.created_by == user[0]:
            raise serializers.ValidationError(
                "Cannot delete creator of group.")
        if not group.users.filter(email=attrs).exists():
            raise serializers.ValidationError('User not part of group.')
