from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that uses email instead of username"""
    username_field = 'email'

    def validate(self, attrs):
        # Use email as the username field
        data = super().validate(attrs)
        data['user'] = UserProfileSerializer(self.user).data
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration - uses email as unique identifier"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone_number', 'username')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': False, 'allow_blank': True, 'allow_null': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        # If username is not provided, use email as username
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'date_joined', 'created_at', 'updated_at')
        read_only_fields = ('id', 'email', 'date_joined', 'created_at', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile - email cannot be changed"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_picture', 'username')
        extra_kwargs = {
            'email': {'read_only': True},  # Email cannot be changed
            'phone_number': {'required': True},
        }

