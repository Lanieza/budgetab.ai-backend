from .models import CustomUser  # Import your custom user model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Use CustomUser model here
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(**validated_data)  # Create user using CustomUser
        if password:
            user.set_password(password)
            user.save()
        return user
