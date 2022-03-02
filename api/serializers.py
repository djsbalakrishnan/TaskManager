from rest_framework import serializers

from django.contrib.auth import get_user_model, authenticate
from .models import ToDo


class UserSerializer(serializers.ModelSerializer):
    """ Serializers for the users Model """
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Create a new user and return it """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """ Update a user instance with new password and return the user instance"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """ Serializer for the user authentication """
    username = serializers.CharField()
    password = serializers.CharField(
        style={
            'input_type': 'password'
        },
        trim_whitespace=False
    )

    def validate(self, attrs):
        """ Validate and authenticate the user """
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            error_message = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(
                error_message, code='authentication')

        attrs['user'] = user
        return attrs


class ToDoSerializer(serializers.ModelSerializer):
    """ Serializer for the ToDo objects """

    class Meta:
        model = ToDo
        fields = ('id', 'title', 'description',
                  'completed', 'due_date', 'created_date',)
        read_only_fields = ('id',)
