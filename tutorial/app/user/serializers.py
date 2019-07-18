from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = [
            'pk',
            'username',
            'email',
            'first_name'
        ]

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    is_create_new_password = serializers.NullBooleanField(required=False)
    role = serializers.IntegerField(required=False)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )
        user_obj = User.objects.filter(email=email, is_active=True).first()
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        return {
            'email': user.email,
            'role':user.role,
            'is_create_new_password': user.is_create_new_password,
            'token': user.token,
        }


class ForgotPasswordSerialzier(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    email = serializers.EmailField(max_length=255)
    
    class Meta:
        model = User
        fields = ('email',)

    def validate(self, validated_data):
        """ validate email for forgot password """

        user = User()
        user = User.objects.filter(email=validated_data['email']).first()
        if not user:
            raise serializer.ValidationError(
                {"email": "Email does not exist in the system."})

        return validated_data


class ResetPassWordSerializer(serializers.ModelSerializer):
    """ Reset password serializer """

    password = serializers.CharField(required=True, max_length=20)

    class Meta:
        model = User
        fields = ('password',)


class ChangePassWordSerializer(serializers.ModelSerializer):
    """ Change password serializer """
   
    old_password = serializers.CharField(required=True, max_length=20)
    new_password = serializers.CharField(required=True, max_length=20)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate(self, validated_data):
        """ check old and new password are not same """

        if validated_data['old_password'] == validated_data['new_password']:
            raise serializers.ValidationError(
                'Old password and new password must not be same')

        return validated_data