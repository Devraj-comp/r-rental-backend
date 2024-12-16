from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.decorators import api_view
from .models import UserProfile





class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only = True)
    email = serializers.EmailField(source = 'user.email', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['role', 'username', 'email']
        # fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    # role = serializers.ChoiceField(choices=[('admin', 'Admin'), ('renter', 'Renter')])
    role = serializers.SerializerMethodField()
    profile = UserProfileSerializer(read_only = True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'profile']
    
    def get_role(self, obj):
        return obj.userprofile.role if hasattr(obj, 'userprofile') else None

    def create(self, validated_data):
        role = validated_data.get('role', 'renter')

        if role == 'admin':
            user = User.objects.create_superuser(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
        else:
            user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
            )
        
        user.save()
        user_profile = UserProfile.objects.create(user=user, role=role)
        user_profile.save()

        return user

class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

