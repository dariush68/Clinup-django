import string
import random
from random import randint
from rest_framework import permissions
import requests
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from kavenegar import KavenegarAPI, APIException, HTTPException
from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from CheckupServer.settings import KAVENEGAR_APIKEY
from Core.models import User
from . import serializers
from .permissions import IsOwner


jibit_base_url = 'https://napi.jibit.ir/ide'
jibit_headers = {'Content-Type': 'application/json'}


def jibit_token_generate():

    __keys = {
        "apiKey": "lKPuXGaPQ6",
        "secretKey": "QONksnNy1KXwAp0hviZFW1aQC"
    }
    jibit_token_response = requests.post(url=f'{jibit_base_url}/v1/tokens/generate', headers=jibit_headers, json=__keys)
    jresponse = jibit_token_response.json()
    if jibit_token_response.status_code == 200:
        Token = Response({"accessToken": jresponse['accessToken'], "refreshToken": jresponse['refreshToken']})
        token_file = open("JibitAccessToken.txt", "w")
        token_file.write(jresponse['accessToken'])
        token_file.close()
    else:
        Token = Response({"code": jresponse['code'], "message": jresponse['message']})

    return Token.data


def password_generator():

    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    length = int(13)

    random.shuffle(characters)

    password_list = []
    for i in range(length):
        password_list.append(random.choice(characters))

    random.shuffle(password_list)

    password = "".join(password_list)

    return password


class UserInfoView(RetrieveUpdateAPIView):
    """Show detailed of user"""
    serializer_class = serializers.UserUpdateSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class SignUpAPIView(APIView):
    """
    User signup API
    """
    serializer_class = serializers.UserSignUpSerializer

    def post(self, request):
        serializer = serializers.UserSignUpSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = get_user_model().objects.get(phone_number=serializer.validated_data['phone_number'])
                if user.is_active:
                    user.generated_token = randint(100000, 999999)
                    user.save()
                    try:
                        api = KavenegarAPI(KAVENEGAR_APIKEY)
                        # params = {'receptor': serializer.validated_data['phone_number'],
                        #           'message': 'دکتر گریفین\n' + 'کد ورود به برنامه:' + str(
                        #               user.generated_token)}
                        # response = api.sms_send(params)
                        params = {'receptor': serializer.validated_data['phone_number'],
                                  'template': 'GriffinLoginVerify', 'token': str(user.generated_token), 'type': 'sms'}
                        response = api.verify_lookup(params)
                        return Response({"message": "کد ورود با موفقیت ارسال شد."})

                    except APIException:
                        return Response(
                            {
                                'error': 'ارسال کد ورود با مشکل مواجه شده است',
                                'type': 'APIException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except HTTPException:
                        return Response(
                            {
                                'error': 'ارسال کد ورود با مشکل مواجه شده است',
                                'type': 'HTTPException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    # user.set_password(serializer.validated_data['password'])
                    password = password_generator()
                    user.set_password(password)
                    user.generated_token = randint(100000, 999999)
                    user.save()
                    try:
                        api = KavenegarAPI(KAVENEGAR_APIKEY)
                        # params = {'receptor': serializer.validated_data['phone_number'],
                        #           'message': 'دکتر گریفین\n' + 'کد تایید:' + str(
                        #               user.generated_token)}
                        # response = api.sms_send(params)
                        params = {'receptor': serializer.validated_data['phone_number'],
                                  'template': 'GriffinSignInVerify', 'token': str(user.generated_token), 'type': 'sms'}
                        response = api.verify_lookup(params)
                        return Response({"message": "کد تایید با موفقیت ارسال شد."})

                    except APIException:
                        return Response(
                            {
                                'error': 'ارسال کد تایید با مشکل مواجه شده است',
                                'type': 'APIException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except HTTPException:
                        return Response(
                            {
                                'error': 'ارسال کد تایید با مشکل مواجه شده است',
                                'type': 'HTTPException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
            except get_user_model().DoesNotExist:
                phone_number = serializer.validated_data['phone_number']
                user = User(
                    phone_number=phone_number,
                )
                # password = serializer.validated_data['password']
                password = password_generator()
                user.is_active = False
                user.set_password(password)
                user.generated_token = randint(100000, 999999)
                user.save()
                try:
                    api = KavenegarAPI(KAVENEGAR_APIKEY)
                    # params = {'receptor': serializer.validated_data['phone_number'],
                    #           'message': 'دکتر گریفین\n' + 'کد تایید:' + str(user.generated_token)}
                    # response = api.sms_send(params)
                    params = {'receptor': serializer.validated_data['phone_number'],
                              'template': 'GriffinSignInVerify', 'token': str(user.generated_token), 'type': 'sms'}
                    response = api.verify_lookup(params)
                    return Response({"message": "کد تایید با موفقیت ارسال شد."})

                except APIException:
                    return Response(
                        {
                            'error': 'ارسال کد تایید با مشکل مواجه شده است',
                            'type': 'APIException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except HTTPException:
                    return Response(
                        {
                            'error': 'ارسال کد تایید با مشکل مواجه شده است',
                            'type': 'HTTPException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendSignUpTokenAPIView(APIView):
    """
    User verification via sms
    """

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        if user:
            serializer = serializers.ResendSignUpTokenSerializer(user, data=data)
            if serializer.is_valid():
                serializer.validated_data['generated_token'] = randint(100000, 999999)
                user.save()
                try:
                    api = KavenegarAPI(KAVENEGAR_APIKEY)
                    params = {'receptor': serializer.validated_data['phone_number'],
                              'message': 'دکتر گریفین\n' + 'کد تایید:' + str(serializer.validated_data['generated_token'])}
                    response = api.sms_send(params)
                    return Response({"message": "ارسال مجدد کد تایید با موفقیت انجام شد."})

                except APIException:
                    return Response(
                        {
                            'error': 'ارسال کد تایید با مشکل مواجه شده است',
                            'type': 'APIException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except HTTPException:
                    return Response(
                        {
                            'error': 'ارسال کد تایید با مشکل مواجه شده است',
                            'type': 'HTTPException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response({"user": "چنین کاربری وجود ندارد"})


class UserPhoneRegisterAPIView(APIView):
    """
    User verification via sms
    """

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        if user:
            serializer = serializers.UserPhoneRegisterSerializer(user, data=data)
            if serializer.is_valid():
                if serializer.data['generated_token'] == int(data.get("generated_token")):
                    if not user.is_active:
                        user.is_active = True
                        user.generated_token = None
                        user.save()
                        refresh = RefreshToken.for_user(user)
                        return Response({
                            "user": "verified and logged in successfully",
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        })
                    else:
                        user.generated_token = None
                        user.save()
                        refresh = RefreshToken.for_user(user)
                        return Response({
                            "user": "logged in successfully",
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        })
                else:
                    return Response(
                        {
                            'error': 'کد وارد شده اشتباه است'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserNationalCodeVerifyAPIView(APIView):
    """
    User NationalCode verification via code sent by sms
    """

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        if user:
            serializer = serializers.UserNationalCodeVerifySerializer(user, data=data)
            if serializer.is_valid():
                if serializer.data['generated_authentication_token'] == int(data.get("generated_authentication_token")):
                    user.national_code = data.get("national_code")
                    user.national_code_approval = True
                    user.generated_authentication_token = None
                    user.save()
                    return Response(
                        {
                            'matched': 'احراز هویت با موفقیت انجام شد'
                        }
                    )
                else:
                    return Response(
                        {
                            'error': 'کد وارد شده اشتباه است'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserNationalCodeRegisterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    """
    User NationalCode Approval via sms
    """

    def put(self, request):
        data = request.data
        phone_number = data['phone_number']
        national_code = data['national_code']
        user = get_object_or_404(get_user_model(), phone_number=phone_number)
        if user:
            serializer = serializers.UserNationalCodeRegisterSerializer(user, data=data)
            if serializer.is_valid():

                token_file = open("JibitAccessToken.txt")
                access_token = token_file.read()
                token_file.close()

                jibit_auth_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                }

                match_response = requests.get(url=f'{jibit_base_url}/v1/services/matching?'
                                                  f'nationalCode={national_code}'
                                                  f'&mobileNumber={phone_number}',
                                              headers=jibit_auth_headers)

                jmatch_response = match_response.json()

                if match_response.status_code == 200:
                    if jmatch_response['matched'] == True:
                        # user.national_code = data.get("national_code")
                        # user.national_code_approval = True
                        user.generated_authentication_token = randint(100000, 999999)
                        user.save()
                        try:
                            api = KavenegarAPI(KAVENEGAR_APIKEY)
                            params = {'receptor': phone_number,
                                      'template': 'GriffinNationalCodeApproval', 'token': str(user.generated_authentication_token),
                                      'type': 'sms'}
                            response = api.verify_lookup(params)
                            return Response({'matched': 'کد احراز هویت با موفقیت ارسال شد.'})

                        except APIException:
                            return Response(
                                {
                                    'error': 'ارسال کد احراز هویت با مشکل مواجه شده است',
                                    'type': 'APIException'
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        except HTTPException:
                            return Response(
                                {
                                    'error': 'ارسال کد احراز هویت با مشکل مواجه شده است',
                                    'type': 'HTTPException'
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        # return Response(
                        #     {
                        #         'matched': 'احراز هویت با موفقیت انجام شد'
                        #     }
                        # )
                    else:
                        return Response(
                            {
                                'not matched': 'مالک کد ملی و شماره همراه مطابقت ندارند'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                else:
                    Token = jibit_token_generate()

                    if Token['accessToken']:

                        token_file = open("JibitAccessToken.txt")
                        access_token = token_file.read()
                        token_file.close()

                        jibit_auth_headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {access_token}'
                        }

                        match_response = requests.get(url=f'{jibit_base_url}/v1/services/matching?'
                                                          f'nationalCode={national_code}'
                                                          f'&mobileNumber={phone_number}',
                                                      headers=jibit_auth_headers)

                        jmatch_response = match_response.json()

                        if match_response.status_code == 200:
                            if jmatch_response['matched'] == True:
                                # user.national_code = data.get("national_code")
                                # user.national_code_approval = True
                                user.generated_authentication_token = randint(100000, 999999)
                                user.save()
                                try:
                                    api = KavenegarAPI(KAVENEGAR_APIKEY)
                                    params = {'receptor': phone_number,
                                              'template': 'GriffinNationalCodeApproval', 'token': str(user.generated_authentication_token),
                                              'type': 'sms'}
                                    response = api.verify_lookup(params)
                                    return Response({'matched': 'کد احراز هویت با موفقیت ارسال شد.'})

                                except APIException:
                                    return Response(
                                        {
                                            'error': 'ارسال کد احراز هویت با مشکل مواجه شده است',
                                            'type': 'APIException'
                                        },
                                        status=status.HTTP_400_BAD_REQUEST
                                    )
                                except HTTPException:
                                    return Response(
                                        {
                                            'error': 'ارسال کد احراز هویت با مشکل مواجه شده است',
                                            'type': 'HTTPException'
                                        },
                                        status=status.HTTP_400_BAD_REQUEST
                                    )
                                # return Response(
                                #     {
                                #         'matched': 'احراز هویت با موفقیت انجام شد'
                                #     }
                                # )
                            else:
                                return Response(
                                    {
                                        'not matched': 'مالک کد ملی و شماره همراه مطابقت ندارند'
                                    },
                                    status=status.HTTP_400_BAD_REQUEST
                                )

                        else:
                            return Response(
                                {
                                    'error': jmatch_response['code'],
                                    'message': jmatch_response['message']
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    elif Token['message']:
                        return Response(
                            {
                                'error': Token['code'],
                                'message': Token['message']
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = serializers.ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["رمز عبور فعلی نادرست میباشد!"]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPassForgotTokenAPIView(APIView):
    """
    Password Forget Operation, Step 1, send Token via SMS
    """

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])

        if user:
            serializer = serializers.ResendSignUpTokenSerializer(user, data=data)
            if serializer.is_valid():
                serializer.validated_data['generated_token'] = randint(100000, 999999)
                user.generated_token = serializer.validated_data['generated_token']
                user.save()
                try:
                    api = KavenegarAPI(KAVENEGAR_APIKEY)
                    params = {'receptor': serializer.validated_data['phone_number'],
                              'message': 'دکتر گریفین\n' + 'کد تغییر رمز عبور:' + str(serializer.validated_data['generated_token'])}
                    response = api.sms_send(params)
                    return Response({"message": "توکن sms با موفقیت ارسال شد."})

                except APIException:
                    return Response(
                        {
                            'error': 'ارسال کد تغییر رمز عبور با مشکل مواجه شده است',
                            'type': 'APIException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except HTTPException:
                    return Response(
                        {
                            'error': 'ارسال کد تغییر رمز عبور با مشکل مواجه شده است',
                            'type': 'HTTPException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response({"user": "چنین کاربری وجود ندارد"})


class VerifyPassForgotTokenAPIView(APIView):
    """
    Password Forget Operation, Step 2, Verify token and change password
    """

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        print(user)
        if user:
            serializer = serializers.UserPassForgotSerializer(user, data=data)
            if serializer.is_valid():
                if serializer.data['generated_token'] == int(data.get("generated_token")):

                    user.set_password(data.get("password"))
                    user.save()
                    return Response({"user": "Change password successfully"})
                else:
                    return Response(
                        {
                            'error': 'The entered token is invalid'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
