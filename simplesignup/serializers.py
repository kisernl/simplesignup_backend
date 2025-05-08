# simplesignup/serializers.py
from rest_framework import serializers
from .models import User, Event 
from django.contrib.auth.hashers import make_password
from rest_framework.serializers import SerializerMethodField
# from django.contrib.auth import get_user_model # not currently used

# User = get_user_model() # not currently used

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # This Meta class correctly references custom User model
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'registration_date', 'is_active']
        # 'password' is intentionally excluded for registration

    def create(self, validated_data):
        # Create a user with an unusable password for passwordless login
        # User.objects.create_user correctly uses the manager of the Meta.model
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=make_password(None)  # Set an unusable password
        )
        return user

class EventSerializer(serializers.ModelSerializer):
    creator = SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['creator']

    def get_creator(self, obj):
        """
        Get the creator (User) of the event.
        """
        # This accesses the creator field of the Event instance, which is the custom User model
        return obj.creator.id # or obj.creator.pk

    def create(self, validated_data):
        """
        Create and return a new Event instance, given the validated data.
        """
        request = self.context.get('request')
        user = request.user if request else None
        validated_data['creator'] = user
        event = Event.objects.create(**validated_data)
        return event
