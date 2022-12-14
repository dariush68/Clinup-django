import string
import random
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from random import randint
from kavenegar import KavenegarAPI, APIException, HTTPException
from CheckupServer.settings import KAVENEGAR_APIKEY
from rest_framework_simplejwt.tokens import RefreshToken
from Core import models
from django.shortcuts import get_object_or_404
from . import serializer
from Core.api.permissions import IsCreationOrIsAuthenticated, IsOwner, IsUserOwnerOrSupervisor, IsClinicOwner,\
    IsClinicMediaAndInfoOwner, IsCheckupOwner, IsQuestionShareOwner, IsQuestionOptionAndOrganOwner,\
    IsQuestionOptionNumEqDatOwner, IsQuestionAnswerOwner, IsPatientSupervisor, IsSupervisorOwner


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


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


class ClinicGroupViewset(viewsets.ModelViewSet):
    queryset = models.ClinicGroup.objects.all()
    serializer_class = serializer.ClinicGroupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class UserViewset(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsCreationOrIsAuthenticated, IsUserOwnerOrSupervisor)

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date_joined')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(phone_number__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(first_name__in=list)
                | Q(last_name__in=list)
                | Q(email__icontains=query)
                | Q(national_code__icontains=query)
            ).distinct()

        query_user_patients = self.request.GET.get("user_patients")
        if query_user_patients is not None:
            try:
                user = models.User.objects.get(
                    Q(pk__exact=query_user_patients)
                )

            except models.User.DoesNotExist:
                user = None

            user_patients = []
            s_users = models.Supervisor.objects.filter(user=user)
            for s_user in s_users:
                user_patients.append(s_user.patient.user.id)

            qs = qs.filter(
                Q(pk__in=user_patients)
            ).distinct()

        return qs


class RelativeTypeViewset(viewsets.ModelViewSet):
    queryset = models.RelativeType.objects.all()
    serializer_class = serializer.RelativeTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_on')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class PatientProfileViewset(viewsets.ModelViewSet):
    queryset = models.PatientProfile.objects.all()
    serializer_class = serializer.PatientProfileSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPatientSupervisor, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_on')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__first_name__in=list)
                | Q(user__last_name__in=list)
            ).distinct()

        query_undercare = self.request.GET.get("undercare")
        if query_undercare is not None:
            qs = qs.filter(
                Q(supervisor_patient__user__id__exact=query_undercare)
            ).distinct()
        return qs


class SupervisorViewset(viewsets.ModelViewSet):
    queryset = models.Supervisor.objects.all()
    serializer_class = serializer.SupervisorSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSupervisorOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__first_name__in=list)
                | Q(user__last_name__in=list)
            ).distinct()
        return qs


class SupervisorAPIView(APIView):
    """
    Supervisor API
    """
    serializer_class = serializer.SupervisorSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request):
        serializerr = serializer.SupervisorSerializer(data=request.data)

        if serializerr.is_valid():
            try:
                patient_user = get_user_model().objects.get(phone_number=serializerr.validated_data['patient_number'])
                if patient_user.is_active:
                    patient_user.generated_token = randint(100000, 999999)
                    patient_user.save()
                    try:
                        api = KavenegarAPI(KAVENEGAR_APIKEY)
                        params = {'receptor': patient_user.phone_number,
                                  'template': 'GriffinSupervisorVerify', 'token': str(patient_user.generated_token),
                                  'type': 'sms'}
                        response = api.verify_lookup(params)
                        return Response({"message": "کد ثبت و احراز هویت بیمار با موفقیت ارسال شد."})

                    except APIException:
                        return Response(
                            {
                                'error': 'ارسال کد با مشکل مواجه شده است',
                                'type': 'APIException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except HTTPException:
                        return Response(
                            {
                                'error': 'ارسال کد با مشکل مواجه شده است',
                                'type': 'HTTPException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    password = password_generator()
                    patient_user.set_password(password)
                    patient_user.generated_token = randint(100000, 999999)
                    patient_user.save()
                    try:
                        api = KavenegarAPI(KAVENEGAR_APIKEY)
                        params = {'receptor': patient_user.phone_number,
                                  'template': 'GriffinSupervisorVerify', 'token': str(patient_user.generated_token),
                                  'type': 'sms'}
                        response = api.verify_lookup(params)
                        return Response({"message": "کد ثبت و احراز هویت بیمار با موفقیت ارسال شد."})

                    except APIException:
                        return Response(
                            {
                                'error': 'ارسال کد با مشکل مواجه شده است',
                                'type': 'APIException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except HTTPException:
                        return Response(
                            {
                                'error': 'ارسال کد با مشکل مواجه شده است',
                                'type': 'HTTPException'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
            except get_user_model().DoesNotExist:
                patient_number = serializerr.validated_data['patient_number']
                patient_user = models.User(
                    phone_number=patient_number,
                )
                password = password_generator()
                patient_user.is_active = False
                patient_user.set_password(password)
                patient_user.generated_token = randint(100000, 999999)
                patient_user.save()
                try:
                    api = KavenegarAPI(KAVENEGAR_APIKEY)
                    params = {'receptor': patient_user.phone_number,
                              'template': 'GriffinSupervisorVerify', 'token': str(patient_user.generated_token),
                              'type': 'sms'}
                    response = api.verify_lookup(params)
                    return Response({"message": "کد ثبت و احراز هویت بیمار با موفقیت ارسال شد."})

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
            return Response(serializerr.errors, status=status.HTTP_400_BAD_REQUEST)


class SupervisorRegisterAPIView(APIView):
    """
    Supervisor verification via sms
    """
    permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request):
        data = request.data
        patient_user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        if patient_user:
            serializerr = serializer.SupervisorRegisterSerializer(patient_user, data=data)
            if serializerr.is_valid():
                relativeType = get_object_or_404(models.RelativeType, id=serializerr.initial_data['relativeType'])
                if serializerr.data['generated_token'] == int(data.get("generated_token")):
                    if not patient_user.is_active:
                        patient_user.is_active = True
                        patient_user.generated_token = None
                        patient_user.save()
                        refresh = RefreshToken.for_user(patient_user)
                        patient, cp = models.PatientProfile.objects.get_or_create(user=patient_user)
                        patient.save()
                        supervisor, cs = models.Supervisor.objects.get_or_create(
                            user=request.user, relativeType=relativeType,
                            patient=patient, patient_number=patient_user.phone_number)
                        supervisor.save()
                        return Response({
                            "status": "افزودن بیمار به لیست افراد تحت مراقبت شما با موفقیت انجام شد",
                            "patient_user_id": patient_user.id,
                            "patient_id": patient.id,
                            "patient_refresh": str(refresh),
                            "patient_access": str(refresh.access_token),
                        })
                    else:
                        patient_user.generated_token = None
                        patient_user.save()
                        refresh = RefreshToken.for_user(patient_user)
                        patient, cp = models.PatientProfile.objects.get_or_create(user=patient_user)
                        print(patient)
                        patient.save()
                        supervisor, cs = models.Supervisor.objects.get_or_create(
                            user=request.user, relativeType=relativeType,
                            patient=patient, patient_number=patient_user.phone_number)
                        supervisor.save()
                        return Response({
                            "status": "افزودن بیمار به لیست افراد تحت مراقبت شما با موفقیت انجام شد",
                            "patient_user_id": patient_user.id,
                            "patient_id": patient.id,
                            "patient_refresh": str(refresh),
                            "patient_access": str(refresh.access_token),
                        })
                else:
                    return Response(
                        {
                            'error': 'کد وارد شده اشتباه است'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(serializerr.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorViewset(viewsets.ModelViewSet):
    queryset = models.Doctor.objects.all()
    serializer_class = serializer.DoctorSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(specialyTitle__icontains=query)
                | Q(user__phone_number=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(specialyTitle__in=list)
                | Q(user__first_name__in=list)
                | Q(user__last_name__in=list)
            ).distinct()
        return qs


class ClinicViewset(viewsets.ModelViewSet):
    queryset = models.Clinic.objects.all()
    serializer_class = serializer.ClinicSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsClinicOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(clinicGroup__title__icontains=query)
                | Q(title__icontains=query)
            ).distinct()

        query_oc = self.request.GET.get("organsClinic")
        if query_oc is not None:

            list = query_oc.split(" ")
            question_share = models.QuestionShare.objects.filter(
                Q(questionOrgans_questionShare__organ__name__in=list)
            ).distinct()
            a_key = "clinic"
            list_of_dicts = question_share.values('clinic')
            values_of_key = [a_dict[a_key] for a_dict in list_of_dicts]
            qs = qs.filter(
                Q(pk__in=values_of_key)
            ).distinct()

        return qs


class RealClinicViewset(viewsets.ModelViewSet):
    queryset = models.RealClinic.objects.all()
    serializer_class = serializer.RealClinicSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(address__icontains=query)
                | Q(name__in=list)
                | Q(description__in=list)
                | Q(address__in=list)
            ).distinct()
        return qs


class RealDoctorViewset(viewsets.ModelViewSet):
    queryset = models.RealDoctor.objects.all()
    serializer_class = serializer.RealDoctorSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(specialyTitle__icontains=query)
                | Q(description__icontains=query)
                | Q(address__icontains=query)
                | Q(name__in=list)
                | Q(specialyTitle__in=list)
                | Q(description__in=list)
                | Q(address__in=list)
            ).distinct()
        return qs


class MediaViewset(viewsets.ModelViewSet):
    queryset = models.Media.objects.all()
    serializer_class = serializer.MediaSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(name__in=list)
            ).distinct()

        return qs


class ClinicMediaViewset(viewsets.ModelViewSet):
    queryset = models.ClinicMedia.objects.all()
    serializer_class = serializer.ClinicMediaSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsClinicMediaAndInfoOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(clinic__title__icontains=query)
                | Q(media__name__icontains=query)
                | Q(clinic__title__in=list)
                | Q(media__name__in=list)
            ).distinct()

        query_category = self.request.GET.get("category")
        if query_category is not None:
            qs = qs.filter(
                Q(media__category__exact=query_category)
            ).distinct()

        query_clinic = self.request.GET.get("clinic")
        if query_clinic is not None:
            qs = qs.filter(
                Q(clinic__id__exact=query_clinic)
            ).distinct()

        query_doctor = self.request.GET.get("doctor")
        if query_doctor is not None:
            qs = qs.filter(
                Q(clinic__agent__id__exact=query_doctor)
            ).distinct()
        return qs


class QuestionShareMediaViewset(viewsets.ModelViewSet):
    queryset = models.QuestionShareMedia.objects.all()
    serializer_class = serializer.QuestionShareMediaSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionOptionAndOrganOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            list = query.split(" ")
            qs = qs.filter(
                Q(media__name__icontains=query)
                | Q(media__name__in=list)
            ).distinct()

        return qs


class CheckupViewset(viewsets.ModelViewSet):
    queryset = models.Checkup.objects.all()
    serializer_class = serializer.CheckupSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCheckupOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(clinic__title__icontains=query)
                | Q(title__icontains=query)
            ).distinct()
        query_patient = self.request.GET.get("patient")
        if query_patient is not None:
            # list = query_patient.split(" ")
            qs = qs.filter(
                Q(patientProfile__user__id__exact=query_patient)
                # Q(patientProfile__user__first_name__icontains=query_patient)
                # | Q(patientProfile__user__last_name__icontains=query_patient)
                # | Q(patientProfile__user__first_name__in=list)
                # | Q(patientProfile__user__last_name__in=list)
            ).distinct()
        return qs


class ClinicCheckupViewset(viewsets.ModelViewSet):
    queryset = models.ClinicCheckup.objects.all()
    serializer_class = serializer.ClinicCheckupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(clinic__title__icontains=query)
                | Q(title__icontains=query)
            ).distinct()
        query_clinic = self.request.GET.get("clinic")
        if query_clinic is not None:
            # list = query_patient.split(" ")
            qs = qs.filter(
                Q(clinic__id__exact=query_clinic)
                # Q(patientProfile__user__first_name__icontains=query_patient)
                # | Q(patientProfile__user__last_name__icontains=query_patient)
                # | Q(patientProfile__user__first_name__in=list)
                # | Q(patientProfile__user__last_name__in=list)
            ).distinct()
        return qs


class CheckupFlowchartViewset(viewsets.ModelViewSet):
    queryset = models.CheckupFlowchart.objects.all()
    serializer_class = serializer.CheckupFlowchartSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()

        query_clinic = self.request.GET.get("clinic")
        if query_clinic is not None:
            qs = qs.filter(
                Q(clinic_checkup__clinic__id__exact=query_clinic)
            ).distinct()

        query_clinicCheckup = self.request.GET.get("clinicCheckup")
        if query_clinicCheckup is not None:
            qs = qs.filter(
                Q(clinic_checkup__id__exact=query_clinicCheckup)
            ).distinct()
        return qs


class CheckupAnalyzeViewset(viewsets.ModelViewSet):
    queryset = models.CheckupAnalyze.objects.all()
    serializer_class = serializer.CheckupAnalyzeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()

        query_clinic = self.request.GET.get("clinic")
        if query_clinic is not None:
            qs = qs.filter(
                Q(clinic_checkup__clinic__id__exact=query_clinic)
            ).distinct()

        query_clinicCheckup = self.request.GET.get("clinicCheckup")
        if query_clinicCheckup is not None:
            qs = qs.filter(
                Q(clinic_checkup__id__exact=query_clinicCheckup)
            ).distinct()
        return qs


class InterpretationViewset(viewsets.ModelViewSet):
    queryset = models.Interpretation.objects.all()
    serializer_class = serializer.InterpretationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(text__icontains=query)
            ).distinct()
        return qs


class SuggestionViewset(viewsets.ModelViewSet):
    queryset = models.Suggestion.objects.all()
    serializer_class = serializer.SuggestionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(interpretation__text__icontains=query)
            ).distinct()
        return qs


class JobViewset(viewsets.ModelViewSet):
    queryset = models.Job.objects.all()
    serializer_class = serializer.JobSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class IllnessViewset(viewsets.ModelViewSet):
    queryset = models.Illness.objects.all()
    serializer_class = serializer.IllnessSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class DrugViewset(viewsets.ModelViewSet):
    queryset = models.Drug.objects.all()
    serializer_class = serializer.DrugSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class DrugAmountViewset(viewsets.ModelViewSet):
    queryset = models.DrugAmount.objects.all()
    serializer_class = serializer.DrugAmountSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class DrugInstructionViewset(viewsets.ModelViewSet):
    queryset = models.DrugInstruction.objects.all()
    serializer_class = serializer.DrugInstructionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class PatientIllnessViewset(viewsets.ModelViewSet):
    queryset = models.PatientIllness.objects.all()
    serializer_class = serializer.PatientIllnessSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(illness__title__icontains=query)
            ).distinct()
        return qs


class PatientFamilyIllnessViewset(viewsets.ModelViewSet):
    queryset = models.PatientFamilyIllness.objects.all()
    serializer_class = serializer.PatientFamilyIllnessSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(illness__title__icontains=query)
            ).distinct()
        return qs


class PatientDrugViewset(viewsets.ModelViewSet):
    queryset = models.PatientDrug.objects.all()
    serializer_class = serializer.PatientDrugSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(illness__title__icontains=query)
            ).distinct()
        return qs


class PatientJobViewset(viewsets.ModelViewSet):
    queryset = models.PatientJob.objects.all()
    serializer_class = serializer.PatientJobSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(illness__title__icontains=query)
            ).distinct()
        return qs


class PatientBiographyViewset(viewsets.ModelViewSet):
    queryset = models.PatientBiography.objects.all()
    serializer_class = serializer.PatientBiographySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(illness__title__icontains=query)
            ).distinct()
        return qs


class MedicalRecordViewset(viewsets.ModelViewSet):
    queryset = models.MedicalRecord.objects.all()
    serializer_class = serializer.MedicalRecordSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(illness__title__icontains=query)
            ).distinct()
        return qs


class OrganViewset(viewsets.ModelViewSet):
    queryset = models.Organ.objects.all()
    serializer_class = serializer.OrganSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(name__icontains=query)
            ).distinct()
        return qs


class QuestionOptionEquationViewset(viewsets.ModelViewSet):
    queryset = models.QuestionOptionEquation.objects.all()
    serializer_class = serializer.QuestionOptionEquationSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionOptionNumEqDatOwner, ]


class QuestionOptionNumberViewset(viewsets.ModelViewSet):
    queryset = models.QuestionOptionNumber.objects.all()
    serializer_class = serializer.QuestionOptionNumberSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionOptionNumEqDatOwner, ]


class QuestionOptionDateViewset(viewsets.ModelViewSet):
    queryset = models.QuestionOptionDate.objects.all()
    serializer_class = serializer.QuestionOptionDateSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionOptionNumEqDatOwner, ]


class QuestionOrganViewset(viewsets.ModelViewSet):
    queryset = models.QuestionOrgan.objects.all()
    serializer_class = serializer.QuestionOrganSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionOptionAndOrganOwner, ]


class QuestionAnswerViewset(viewsets.ModelViewSet):
    queryset = models.QuestionAnswer.objects.all()
    serializer_class = serializer.QuestionAnswerSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionAnswerOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')

        # get all answer or filter based on clinicAgent
        is_get_all = False
        query = self.request.GET.get("getAll")
        if query is not None:
            if query == "true" or query == 1 or query:
                is_get_all = True
        if is_get_all is False:
            user = self.request.user
            qs = qs.filter(Q(checkup__clinic__id=user.id)).distinct()

        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(checkup__clinic__id__exact=query)
            ).distinct()

        query_patient = self.request.GET.get("patient")
        if query_patient is not None:
            list = query_patient.split(" ")
            qs = qs.filter(
                Q(checkup__patientProfile__user__first_name__icontains=query_patient)
                | Q(checkup__patientProfile__user__last_name__icontains=query_patient)
                | Q(checkup__patientProfile__user__first_name__in=list)
                | Q(checkup__patientProfile__user__last_name__in=list)
            ).distinct()

        return qs


class QuestionOptionViewset(viewsets.ModelViewSet):
    queryset = models.QuestionOption.objects.all()
    serializer_class = serializer.QuestionOptionSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionOptionAndOrganOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()
        return qs


class QuestionShareViewset(viewsets.ModelViewSet):
    queryset = models.QuestionShare.objects.all()
    serializer_class = serializer.QuestionShareSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionShareOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')

        # get all question or filter based on doctor
        is_get_all = False
        query = self.request.GET.get("getAll")
        # is_get_all = False
        if query is not None:
            if query == "true" or query == 1 or query:
                is_get_all = True
        if is_get_all is False:
            user = self.request.user
            # print(f"filter {user}")
            qs = qs.filter(Q(doctor__user=user.id)).distinct()
            # print(qs)

        query_clinic = self.request.GET.get("clinic")
        if query_clinic is not None:
            qs = qs.filter(
                Q(clinic__id__exact=query_clinic)
            ).distinct()

        query_qlevel = self.request.GET.get('expert_level')
        if query_qlevel is not None:
            qs = qs.filter(
                Q(expert_level__exact=query_qlevel)
            ).distinct()

        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(short_title__icontains=query)
            ).distinct()

        query_organs = self.request.GET.get("organs")
        if query_organs is not None:
            list = query_organs.split(" ")
            qs = qs.filter(
                Q(questionOrgans_questionShare__organ__name__in=list)
            ).distinct()
        return qs


# class LightQuestionShareViewset(viewsets.ModelViewSet):
#     queryset = models.QuestionShare.objects.all()
#     serializer_class = serializer.LightQuestionShareSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
#
#     def get_queryset(self):
#         qs = super().get_queryset().order_by('-id')
#         return qs


# class LightQuestionOptionViewset(viewsets.ModelViewSet):
#     queryset = models.QuestionOption.objects.all()
#     serializer_class = serializer.LightQuestionOptionSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
#
#     def get_queryset(self):
#         qs = super().get_queryset().order_by('-id')
#         return qs


class CompressedQuestionShareViewset(viewsets.ModelViewSet):
    queryset = models.QuestionShare.objects.all()
    serializer_class = serializer.CompressedQuestionShareSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsQuestionShareOwner, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')

        # get all question or filter based on doctor
        is_get_all = False
        query = self.request.GET.get("getAll")
        if query is not None:
            if query == "true" or query == 1 or query:
                is_get_all = True
        if is_get_all is False:
            user = self.request.user
            qs = qs.filter(Q(doctor__user=user.id)).distinct()

        query_clinic = self.request.GET.get("clinic")
        if query_clinic is not None:
            qs = qs.filter(
                Q(clinic__id__exact=query_clinic)
            ).distinct()

        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(short_title__icontains=query)
            ).distinct()

        query_organs = self.request.GET.get("organs")
        if query_organs is not None:
            list = query_organs.split(" ")
            qs = qs.filter(
                Q(questionOrgans_questionShare__organ__name__in=list)
            ).distinct()
        return qs


class AlertsViewset(viewsets.ModelViewSet):
    queryset = models.Alert.objects.all()
    serializer_class = serializer.AlertSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')

        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query)
            ).distinct()

        return qs


class FlowchartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def create(self, request):
        query = request.POST.get("data")
        print(query)
        return Response({"resp": "ok"})


# @api_view(['POST'])
# @permission_classes([AllowAny])
@csrf_exempt
def flowchart(request):
    if request.method == 'POST':
        print(f"in post {request.body}")
        json_data = json.loads(request.body)
        print(json_data)
        print(len(json_data))
        print(json_data[0]['id'])

        for qstShare in json_data:
            print(qstShare)
            try:
                objQstShare = models.QuestionShare.objects.get(id=qstShare['id'])

                objQstShare.chart_is_visible = qstShare['chart_is_visible']
                objQstShare.chart_global_src_ = qstShare['chart_global_src_x']
                objQstShare.chart_global_src_y = qstShare['chart_global_src_y']
                objQstShare.chart_global_des_x = qstShare['chart_global_des_x']
                objQstShare.chart_global_des_y = qstShare['chart_global_des_y']
                objQstShare.is_starter = qstShare['is_starter']
                temp = qstShare['chart_connectQstId']
                if temp != "null" and temp != "":
                    obj = models.QuestionShare.objects.get(id=temp)
                    objQstShare.chart_connectQstId = obj
                objQstShare.chart_branchCount = qstShare['chart_branchCount']
                objQstShare.save()

                for qstOption in qstShare['questionOptions_questionShare']:
                    objQstOption = models.QuestionOption.objects.get(id=qstOption['id'])

                    objQstOption.chart_global_x = qstOption['chart_global_x']
                    objQstOption.chart_global_y = qstOption['chart_global_y']
                    temp = qstOption['chart_connectQstId']
                    if temp != "null" and temp != "":
                        obj = models.QuestionShare.objects.get(id=temp)
                        objQstOption.chart_connectQstId = obj
                    objQstOption.save()
            except:
                print("exception rise")

        return HttpResponse("operation done successfully")
    return HttpResponse("operation failed")
    # return Response({"resp": "ok2"})


@api_view(['POST'])
def create_auth(request):
    serialized = serializer.UserSerializer(data=json.loads(request.body))
    if serialized.is_valid():
        models.User.objects.create_user(
            serialized.validated_data['phone_number'],
            serialized.validated_data['password']
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes((IsAuthenticated, ))
def search(request):
    query = request.GET.get("q")
    results = []
    if query:
        list = query.split(" ")
        doctors = models.Doctor.objects.filter(Q(specialyTitle__icontains=query)
                                               | Q(user__first_name__icontains=query)
                                               | Q(user__last_name__icontains=query)
                                               | Q(user__first_name__in=list)
                                               | Q(user__last_name__in=list))
        clinics = models.Clinic.objects.filter(Q(title__icontains=query))
        ser_doctor = serializer.DoctorSerializer(instance=doctors, many=True)
        ser_clinics = serializer.ClinicSerializer(instance=clinics, many=True)
        results = {
            'doctors': ser_doctor.data,
            'clinics': ser_clinics.data,
        }

    return Response({"resp": results})


@api_view(['GET'])
# @permission_classes((IsAuthenticated, ))
def checkup_result(request):
    query = request.GET.get("q")
    results = []
    interpretations = []
    alerts = []
    suggested_doctors = []
    suggested_clinics = []

    if query:

        checkup = get_object_or_404(models.Checkup, id=query)

        if checkup.patientProfile.user == request.user:

            question_answers = models.QuestionAnswer.objects.filter(Q(checkup_id=query))

            if question_answers:
                for question_answer in question_answers:
                    if question_answer.questionOption.interpretation:
                        interpretations.append(question_answer.questionOption.interpretation)
                    if question_answer.questionOption.alert:
                        alerts.append(question_answer.questionOption.alert.id)
                    if question_answer.questionOption.suggestedDoctor:
                        suggested_doctors.append(question_answer.questionOption.suggestedDoctor.id)
                    if question_answer.questionOption.suggestedClinic:
                        suggested_clinics.append(question_answer.questionOption.suggestedClinic.id)

                alert = models.Alert.objects.filter(Q(pk__in=alerts))
                ser_alert = serializer.AlertSerializer(instance=alert, many=True)
                doctors = models.Doctor.objects.filter(Q(pk__in=suggested_doctors))
                ser_doctors = serializer.DoctorSerializer(instance=doctors, many=True)
                clinics = models.Clinic.objects.filter(Q(pk__in=suggested_clinics))
                ser_clinics = serializer.ClinicSerializer(instance=clinics, many=True)
                results = {
                    'alerts': ser_alert.data,
                    'interpretations': interpretations,
                    'suggestedDoctors': ser_doctors.data,
                    'suggestedClinics': ser_clinics.data,
                }

            else:
                results = {
                    'checkup': 'The selected checkup has no answer'
                }

        else:
            results = {
                'checkup': 'You do not have the permission to see this checkup'
            }

    return Response({"resp": results})
