from rest_framework import serializers
from django.contrib.auth import get_user_model  # If used custom user model
from Core import models
from drf_writable_nested.serializers import WritableNestedModelSerializer

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

    class Meta:
        model = UserModel  # models.User
        fields = [
            'id',
            'phone_number',
            'email',
            'password',
            'first_name',
            'last_name',
            'date_joined',
            'national_code',
            'national_code_approval',
        ]
        read_only_fields = ('is_active', 'is_staff', 'date_joined', 'national_code', 'national_code_approval')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class RelativeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RelativeType
        fields = [
            'id',
            'title',
            'created_on'
        ]


class PatientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    supervisor = serializers.SerializerMethodField(read_only=True)
    supervisor_full_name = serializers.SerializerMethodField(read_only=True)
    supervisor_relativeType = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.PatientProfile
        fields = [
            'id',
            'user_id',
            'full_name',
            'supervisor',
            'supervisor_full_name',
            'supervisor_relativeType',
            'created_on'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_supervisor(self, obj):
        try:
            sup = obj.supervisor_patient.user.id
            return sup
        except models.Supervisor.DoesNotExist:
            return ""

    def get_supervisor_full_name(self, obj):
        try:
            sup_name = obj.supervisor_patient.user.get_full_name()
            return sup_name
        except models.Supervisor.DoesNotExist:
            return ""

    def get_supervisor_relativeType(self, obj):
        try:
            sup_rel = obj.supervisor_patient.relativeType.title
            return sup_rel
        except models.Supervisor.DoesNotExist:
            return ""


class SupervisorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    relativeType_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        patient = models.PatientProfile.objects.get(user__phone_number=validated_data['patient_number'])
        validated_data['patient'] = patient
        return models.Supervisor.objects.create(**validated_data)

    class Meta:
        model = models.Supervisor
        fields = [
            'id',
            'user',
            'name',
            'relativeType',
            'relativeType_name',
            'patient',
            'patient_name',
            'patient_number'
        ]

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_relativeType_name(self, obj):
        return obj.relativeType.title

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()


class SupervisorRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ('phone_number', 'generated_token')


class DoctorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    userPicture = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Doctor
        fields = [
            'id',
            'user',
            'name',
            'systemCode',
            'specialyTitle',
            'userPicture',
            'description'
        ]

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_userPicture(self, obj):
        if obj.user.picture:
            return obj.user.picture.url
        else:
            return None


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Alert
        fields = [
            'id',
            'title',
            'description',
            'severity',
            'reminder_time_scale',
            'reminder_number',
            'reminder_type',
            'created_on'
        ]


class OrganSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Organ
        fields = [
            'id',
            'name',
            'parent',
            'parent_name',
        ]

    def get_parent_name(self, obj):
        if obj.parent:
            return models.Organ.objects.get(id=obj.parent.id).name
        return ""


class ClinicGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClinicGroup
        fields = [
            'id',
            'title',
            'created_on',
        ]


class ClinicSerializer(serializers.ModelSerializer):
    clinicGroupName = serializers.SerializerMethodField(read_only=True)
    agentName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Clinic
        fields = [
            'id',
            'title',
            'clinicGroup',
            'clinicGroupName',
            'agent',
            'agentName',
            'address',
            'description',
            'icon',
            'created_on',
            'long',
            'lat',
        ]

    def get_clinicGroupName(self, obj):
        return obj.clinicGroup.title

    def get_agentName(self, obj):
        return obj.agent.user.get_full_name()


class RealClinicSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RealClinic
        fields = [
            'id',
            'name',
            'description',
            'address',
            'icon',
            'showState',
            'priority',
            'long',
            'lat',
            'created_on',
        ]


class RealDoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RealDoctor
        fields = [
            'id',
            'name',
            'specialyTitle',
            'description',
            'address',
            'icon',
            'showState',
            'priority',
            'long',
            'lat',
            'created_on',
        ]


class MediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Media
        fields = [
            'id',
            'type',
            'category',
            'name',
            'source',
            'created_on',
        ]


class ClinicMediaSerializer(WritableNestedModelSerializer):
    clinicAgentName = serializers.SerializerMethodField(read_only=True)
    clinicName = serializers.SerializerMethodField(read_only=True)
    media = MediaSerializer(many=False)

    class Meta:
        model = models.ClinicMedia
        fields = [
            'id',
            'media',
            'clinic',
            'clinicName',
            'clinicAgentName',
            'created_on',
        ]

    def get_clinicAgentName(self, obj):
        return obj.clinic.agent.user.get_full_name()

    def get_clinicName(self, obj):
        return obj.clinic.title


class QuestionShareMediaSerializer(serializers.ModelSerializer):
    # clinicAgentName = serializers.SerializerMethodField(read_only=True)
    # questionShareTitle = serializers.SerializerMethodField(read_only=True)
    # clinic = serializers.SerializerMethodField(read_only=True)
    # clinicName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.QuestionShareMedia
        fields = [
            'id',
            'media',
            # 'questionShare_id',
            # 'questionShareTitle',
            # 'clinic',
            # 'clinicName',
            # 'clinicAgentName',
            'created_on',
        ]

        depth = 1

    # def get_clinicAgentName(self, obj):
    #     return obj.questionShare.clinic.agent.user.get_full_name()
    #
    # def get_questionShareTitle(self, obj):
    #     return obj.questionShare.title
    #
    # def get_clinic(self, obj):
    #     return obj.questionShare.clinic.id
    #
    # def get_clinicName(self, obj):
    #     return obj.questionShare.clinic.title


class CheckupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = None
        patient = models.PatientProfile.objects.get(user__phone_number=validated_data['patientProfile'])
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        try:
            if patient == user.patient_user:
                validated_data['patientProfile'] = user.patient_user
            elif patient.supervisor_patient.user == user:
                validated_data['patientProfile'] = validated_data['patientProfile']
        except models.PatientProfile.DoesNotExist:
            raise serializers.ValidationError('User is not a patient')
        except models.Supervisor.DoesNotExist:
            raise serializers.ValidationError({'denied': 'Only patient or his supervisor can perform this action'})
        return models.Checkup.objects.create(**validated_data)

    clinicGroupName = serializers.SerializerMethodField(read_only=True)
    agentName = serializers.SerializerMethodField(read_only=True)
    clinicName = serializers.SerializerMethodField(read_only=True)
    clinicCheckupTitle = serializers.SerializerMethodField(read_only=True)
    # patientProfile = serializers.SerializerMethodField(read_only=True)
    patientName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Checkup
        fields = [
            'id',
            'patientProfile',
            'patientName',
            'clinic_checkup',
            'clinicCheckupTitle',
            'clinic',
            'clinicName',
            'clinicGroupName',
            'agentName',
            'title',
            'description',
            'executionDate',
        ]

    def get_clinicGroupName(self, obj):
        return obj.clinic.clinicGroup.title

    def get_clinicName(self, obj):
        return obj.clinic.title

    # def get_clinicCheckupTitle(self, obj):
    #     return obj.clinic_checkup.title

    # def get_patientProfile(self, obj):
    #     return obj.patientProfile.pk

    def get_patientName(self, obj):
        return obj.patientProfile.user.get_full_name()

    def get_agentName(self, obj):
        return obj.clinic.agent.user.get_full_name()


class ClinicCheckupSerializer(serializers.ModelSerializer):
    clinicName = serializers.SerializerMethodField(read_only=True)
    agentName = serializers.SerializerMethodField(read_only=True)
    question_short_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ClinicCheckup
        fields = [
            'id',
            'title',
            'clinic',
            'clinicName',
            'agentName',
            'required_time',
            'required_auth',
            'question_count',
            'approvers',
            'starting_question',
            'question_short_title',
        ]

    def get_agentName(self, obj):
        return obj.clinic.agent.user.get_full_name()

    def get_clinicName(self, obj):
        return obj.clinic.title

    def get_question_short_title(self, obj):
        return obj.starting_question.short_title


class CheckupFlowchartSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CheckupFlowchart
        fields = [
            'id',
            'title',
            'text',
            'clinic_checkup',
        ]


class CheckupAnalyzeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CheckupAnalyze
        fields = [
            'id',
            'title',
            'text',
            'clinic_checkup',
        ]


class InterpretationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Interpretation
        fields = [
            'id',
            'text',
            'checkup_analyze',
        ]


class SuggestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Suggestion
        fields = [
            'id',
            'interpretation',
            'alert',
            'suggestedDoctor',
            'suggestedRealDoctor',
            'suggestedClinic',
            'suggestedRealClinic',
            'suggestedMedia',
        ]


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Job
        fields = [
            'id',
            'title',
        ]


class IllnessSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Illness
        fields = [
            'id',
            'title',
        ]


class DrugSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Drug
        fields = [
            'id',
            'title',
        ]


class DrugAmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DrugAmount
        fields = [
            'id',
            'title',
        ]


class DrugInstructionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DrugInstruction
        fields = [
            'id',
            'title',
        ]


class PatientIllnessSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PatientIllness
        fields = [
            'id',
            'illness',
            'patient',
        ]


class PatientFamilyIllnessSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PatientFamilyIllness
        fields = [
            'id',
            'illness',
            'patient',
            'family_member',
        ]


class PatientDrugSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PatientDrug
        fields = [
            'id',
            'patient',
            'drug',
            'amount',
            'instruction',
        ]


class PatientJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PatientJob
        fields = [
            'id',
            'job',
            'patient',
        ]


class PatientBiographySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PatientBiography
        fields = [
            'id',
            'patient',
            'blood_type',
            'birth_date',
            'landline',
            'marital_status',
            'nationality',
            'education',
            'insurance_type',
            'created_on',
        ]


class MedicalRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MedicalRecord
        fields = [
            'id',
            'patient',
            'height',
            'weight',
            'bmi',
            'systolic_blood_pressure',
            'diastolic_blood_pressure',
            'created_on',
        ]


class QuestionOptionEquationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionOptionEquation
        fields = [
            'id',
            'questionOption',
            'upper_band',
            'lower_band',
        ]
        read_only_fields = ['questionOption', ]


class QuestionOptionNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.QuestionOptionNumber
        fields = [
            'id',
            'questionOption',
            'upper_band',
            'lower_band',
        ]
        read_only_fields = ['questionOption', ]


class QuestionOptionDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.QuestionOptionDate
        fields = [
            'id',
            'questionOption',
            'upper_band',
            'lower_band',
        ]
        read_only_fields = ['questionOption', ]


class QuestionOptionSerializer(WritableNestedModelSerializer):
    questionOptionEquations = QuestionOptionEquationSerializer(many=True)
    questionOptionNumbers = QuestionOptionNumberSerializer(many=True)
    questionOptionDates = QuestionOptionDateSerializer(many=True)
    suggestedDoctorName = serializers.SerializerMethodField(read_only=True)
    suggestedClinicName = serializers.SerializerMethodField(read_only=True)
    alertTitle = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.QuestionOption
        fields = [
            'id',
            'is_branch',
            'title',
            'weight',
            'suggestedDoctor',
            'suggestedDoctorName',
            'suggestedClinic',
            'suggestedClinicName',
            'interpretation',
            'alert',
            'alertTitle',
            'tutorial',
            'questionShare',
            'chart_global_x',
            'chart_global_y',
            'chart_connectQstId',
            'questionOptionEquations',
            'questionOptionNumbers',
            'questionOptionDates',
        ]
        read_only_fields = ['questionShare', ]

    def get_suggestedDoctorName(self, obj):
        if obj.suggestedDoctor:
            return obj.suggestedDoctor.user.get_full_name()
        return ""

    def get_suggestedClinicName(self, obj):
        if obj.suggestedClinic:
            return obj.suggestedClinic.title
        return ""

    def get_alertTitle(self, obj):
        if obj.alert:
            return obj.alert.title
        return ""


class QuestionOrganSerializer(serializers.ModelSerializer):
    organName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.QuestionOrgan
        fields = [
            'id',
            'organ',
            'organName',
            'questionShare',
        ]
        read_only_fields = ['organName', 'questionShare']

    def get_organName(self, obj):
        return obj.organ.name

    def get_questionShareName(self, obj):
        return obj.questionShare.short_title


class QuestionShareSerializer(WritableNestedModelSerializer):
    doctorName = serializers.SerializerMethodField(read_only=True)
    clinicName = serializers.SerializerMethodField(read_only=True)
    # clinicCheckupTitle = serializers.SerializerMethodField(read_only=True)
    questionOrgans_questionShare = QuestionOrganSerializer(many=True)
    questionOptions_questionShare = QuestionOptionSerializer(many=True)
    QuestionShareMedia_questionShares = QuestionShareMediaSerializer(many=True)

    class Meta:
        model = models.QuestionShare
        fields = [
            'id',
            'doctor',
            'doctorName',
            'clinic',
            'clinicName',
            # 'clinic_checkup',
            # 'clinicCheckupTitle',
            'title',
            'short_title',
            'is_starter',
            'expert_level',
            'question_type',
            'prority_type',
            'is_date',
            'is_date_limit',
            'date_limit_num',
            'date_type',
            'is_show_chart',
            'is_equation',
            'equation',
            'is_multiple_choice',
            'chart_is_visible',
            'chart_global_src_x',
            'chart_global_src_y',
            'chart_global_des_x',
            'chart_global_des_y',
            'chart_connectQstId',
            'chart_branchCount',
            'QuestionShareMedia_questionShares',
            'questionOrgans_questionShare',
            'questionOptions_questionShare',
        ]

    def get_doctorName(self, obj):
        return obj.doctor.user.get_full_name()

    def get_clinicName(self, obj):
        return obj.clinic.title

    # def get_clinicCheckupTitle(self, obj):
    #     if obj.clinic_checkup:
    #         return obj.clinic_checkup.title
    #     else:
    #         return ""


# LightQuestionShareSerializer for using in QuestionAnswerSerializer
class LightQuestionShareSerializer(serializers.ModelSerializer):
    doctorName = serializers.SerializerMethodField(read_only=True)
    clinicName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.QuestionShare
        fields = [
            'id',
            'doctorName',
            'clinicName',
            'title',
            'short_title',
            'chart_connectQstId',
        ]

    def get_doctorName(self, obj):
        return obj.doctor.user.get_full_name()

    def get_clinicName(self, obj):
        return obj.clinic.title


# LightQuestionOptionSerializer for using in QuestionAnswerSerializer
class LightQuestionOptionSerializer(serializers.ModelSerializer):
    questionOptionEquations = QuestionOptionEquationSerializer(many=True, read_only=True)
    questionOptionNumbers = QuestionOptionNumberSerializer(many=True, read_only=True)
    questionOptionDates = QuestionOptionDateSerializer(many=True, read_only=True)
    suggestedDoctorName = serializers.SerializerMethodField(read_only=True)
    suggestedClinicName = serializers.SerializerMethodField(read_only=True)
    alertTitle = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.QuestionOption
        fields = [
            'id',
            'is_branch',
            'title',
            'weight',
            'suggestedDoctor',
            'suggestedDoctorName',
            'suggestedClinic',
            'suggestedClinicName',
            'interpretation',
            'alert',
            'alertTitle',
            'tutorial',
            'chart_connectQstId',
            'questionOptionEquations',
            'questionOptionNumbers',
            'questionOptionDates',
        ]

    def get_suggestedDoctorName(self, obj):
        if obj.suggestedDoctor:
            return obj.suggestedDoctor.user.get_full_name()
        return ""

    def get_suggestedClinicName(self, obj):
        if obj.suggestedClinic:
            return obj.suggestedClinic.title
        return ""

    def get_alertTitle(self, obj):
        if obj.alert:
            return obj.alert.title
        return ""


# CompressedQuestionShareSerializer for using in phone frontend
class CompressedQuestionShareSerializer(serializers.ModelSerializer):
    doctorName = serializers.SerializerMethodField(read_only=True)
    clinicName = serializers.SerializerMethodField(read_only=True)
    # clinicCheckupTitle = serializers.SerializerMethodField(read_only=True)
    questionOrgans_questionShare = QuestionOrganSerializer(many=True, read_only=True)
    questionOptions_questionShare = LightQuestionOptionSerializer(many=True, read_only=True)
    QuestionShareMedia_questionShares = QuestionShareMediaSerializer(many=True, read_only=True)

    class Meta:
        model = models.QuestionShare
        fields = [
            'id',
            'title',
            'short_title',
            'is_starter',
            'doctor',
            'doctorName',
            'clinic',
            'clinicName',
            # 'clinic_checkup',
            # 'clinicCheckupTitle',
            'expert_level',
            'question_type',
            'prority_type',
            'is_date',
            'is_date_limit',
            'date_limit_num',
            'date_type',
            'is_show_chart',
            'is_equation',
            'equation',
            'is_multiple_choice',
            'chart_connectQstId',
            'QuestionShareMedia_questionShares',
            'questionOrgans_questionShare',
            'questionOptions_questionShare',
        ]

    def get_doctorName(self, obj):
        return obj.doctor.user.get_full_name()

    def get_clinicName(self, obj):
        return obj.clinic.title

    # def get_clinicCheckupTitle(self, obj):
    #     if obj.clinic_checkup:
    #         return obj.clinic_checkup.title
    #     else:
    #         return ""


class QuestionAnswerSerializer(serializers.ModelSerializer):
    # checkup = CheckupSerializer(many=True)
    # questionShare = LightQuestionShareSerializer(many=True)
    # questionOption = LightQuestionOptionSerializer(many=True)

    class Meta:
        model = models.QuestionAnswer

        fields = [
            'id',
            'checkup',
            'questionShare',
            'questionOption',
        ]
