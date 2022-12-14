from rest_framework import serializers, validators

from Core.models import User


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id',
                  'email',
                  'phone_number',
                  'first_name',
                  'last_name',
                  'picture',
                  'national_code',
                  'national_code_approval',
                  ]
        read_only_fields = ('id',)


class UserSignUpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    # password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    #
    # class Meta:
    #     model = User
    #     fields = ['phone_number', 'password']
    #     extra_kwargs = {
    #         'password': {'write_only': True}
    #     }


class UserNationalCodeRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('phone_number', 'national_code')


class ResendSignUpTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['phone_number', 'generated_token']
        read_only_fields = (
            'generated_token',
        )


class UserPhoneRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('phone_number', 'generated_token')


class UserNationalCodeVerifySerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('phone_number', 'national_code', 'generated_authentication_token')


class UserPassForgotSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('phone_number', 'generated_token', 'password')


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
