from django.db import models
from rest_framework.serializers import ValidationError as SValidationError
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _

from CheckupServer.settings import STATIC_URL
from .userModel.userModel import UserManager, validate_phone_number, validate_image, validate_landline


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that support phone number instead of username
    """

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    phone_number = models.CharField(validators=[validate_phone_number], max_length=11, unique=True)
    email = models.EmailField(_('email address'), blank=True)
    generated_token = models.IntegerField(blank=True, null=True)
    generated_authentication_token = models.IntegerField(blank=True, null=True)
    picture = models.ImageField(upload_to='uploads/image/user', null=True, blank=True, validators=[validate_image])
    national_code = models.CharField(max_length=10, blank=True)
    national_code_approval = models.BooleanField(_('national code approval'), default=False)
    birth_date = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)

    def save(self, *args, **kwargs):
        if not self.picture:
            self.picture = STATIC_URL + 'Core/DefaultPics/user-default-image.jpg'
        super(User, self).save(*args, **kwargs)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Organ(MPTTModel):
    name = models.CharField(max_length=300, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return f'{self.name}'


class RelativeType(models.Model):
    title = models.CharField(max_length=200, unique=True, help_text='نسبت فامیلی')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.title}'


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_user', help_text='کاربر')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.user}'


class Supervisor(models.Model):
    user = models.ForeignKey(User, related_name='supervisor_user', on_delete=models.CASCADE, help_text='کاربر')
    relativeType = models.ForeignKey(RelativeType, related_name='supervisor_relativeType', on_delete=models.CASCADE
                                     , help_text='نسبت فامیلی با بیمار')
    patient = models.OneToOneField(PatientProfile, null=True, blank=True, related_name='supervisor_patient', on_delete=models.CASCADE,
                                help_text='اطلاعات بیمار')
    patient_number = models.CharField(validators=[validate_phone_number], max_length=11, unique=True)

    def save(self, *args, **kwargs):
        self.patient_number = self.patient.user.phone_number
        super(Supervisor, self).save(*args, **kwargs)

    def validate_unique(self, *args, **kwargs):
        super(Supervisor, self).validate_unique(*args, **kwargs)

        qs = self.__class__._default_manager.filter(
            user=self.user,
            relativeType=self.relativeType,
            patient=self.patient
        )

        if not self._state.adding and self.pk is not None:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError({
                NON_FIELD_ERRORS: ['This field is exist', ],
            })

    def __str__(self):
        return f'{self.user} is {self.relativeType} of {self.patient}'


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_user', help_text='کاربر')
    systemCode = models.CharField(max_length=120, blank=True, help_text='کد سیستم')
    specialyTitle = models.CharField(max_length=120, blank=True, help_text='عنوان شخص')
    description = models.TextField(blank=True, help_text='توضیحات')

    def __str__(self):
        return f'{self.user}'


class RealDoctor(models.Model):
    name = models.CharField(max_length=200, help_text='نام پزشک')
    specialyTitle = models.CharField(max_length=120, blank=True, help_text='تخصص')
    description = models.TextField(blank=True, help_text='توضیحات')
    address = models.CharField(max_length=600, blank=True, help_text='آدرس مطب')
    icon = models.ImageField(upload_to='uploads/image/RealDoctorsIcon', null=True, blank=True, help_text='آیکون')
    showState = models.BooleanField(default=True, help_text='وضعیت نمایش')
    priority = models.IntegerField(default=0, help_text='اولویت نمایش')
    long = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=6, help_text='مختصات عرض جغرافیایی')
    lat = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=6, help_text='مختصات طول جغرافیاییک')
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.icon:
            self.icon = STATIC_URL + 'Core/DefaultPics/user-default-image.jpg'
        super(RealDoctor, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class ClinicGroup(models.Model):
    title = models.CharField(max_length=200, unique=True, help_text='عنوان کلینیک')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.title}'


class Clinic(models.Model):
    clinicGroup = models.ForeignKey(to=ClinicGroup, related_name='clinics_clinicGroup', on_delete=models.CASCADE,
                                    help_text='گروه کلینیک')
    agent = models.ForeignKey(to=Doctor, related_name='clinics_agent', on_delete=models.CASCADE, help_text='دکتر مسئول')
    title = models.CharField(max_length=300, unique=True, help_text='نام کلینیک')
    address = models.CharField(max_length=600, blank=True, help_text='آدرس کلینیک')
    description = models.TextField(blank=True, help_text='توضیحات')
    icon = models.ImageField(upload_to='uploads/image/ClinicsIcon', null=True, blank=True, help_text='لوگو کلینیک')
    created_on = models.DateTimeField(auto_now=timezone.now())
    long = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=6, help_text='مختصات عرض جغرافیایی')
    lat = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=6, help_text='مختصات طول جغرافیاییک')

    def save(self, *args, **kwargs):
        if not self.icon:
            self.icon = STATIC_URL + 'Core/DefaultPics/clinic-default-icon.png'
        super(Clinic, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'


SEVERITY_CHOICES = (
    (1, "low"),
    (2, "medium"),
    (3, "high"),
)

REMINDER_TIME_SCALE_CHOICES = (
    ("day", "روز"),
    ("week", "هفته"),
    ("month", "ماه"),
    ("year", "سال"),
)

REMINDER_TYPE_CHOICES = (
    ("sms", "پیامک"),
    ("webNotification", "نوتیفیکیشن در سایت"),
    ("call", "تماس صوتی"),
)


class Alert(models.Model):
    clinic = models.ForeignKey(to=Clinic, related_name='alert_clinic', on_delete=models.CASCADE, help_text='کلینیکی که این مدیا مطعلق به آن است')
    title = models.CharField(max_length=200, help_text='عنوان هشدار')
    description = models.TextField(help_text='متن هشدار')
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=1, help_text='درجه ضرورت هشدار')
    reminder_time_scale = models.CharField(max_length=5, blank=True, choices=REMINDER_TIME_SCALE_CHOICES, help_text='واحد یاداوری هشدار')
    reminder_number = models.PositiveSmallIntegerField(blank=True, help_text='عدد فاصله زمانی یاداور بر حسب اسکیل زمانی انتخاب شده')
    reminder_type = models.CharField(blank=True, max_length=15, choices=REMINDER_TYPE_CHOICES,
                                           help_text='نوع یاداوری هشدار')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.title}'


class MediaType(models.Model):
    title = models.CharField(max_length=200, unique=True, help_text='نوع مدیا مثل تصویر، صوت و فیلم')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.title}'


class MediaCategory(models.Model):
    title = models.CharField(max_length=200, unique=True, help_text='دسته بندی مدیا')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.title}'


class Media(models.Model):
    type = models.ForeignKey(to=MediaType, related_name='medias', on_delete=models.CASCADE, help_text='نوع مدیا')
    category = models.ForeignKey(to=MediaCategory, related_name='media_category', on_delete=models.CASCADE,
                                 help_text='دسته بندی مدیا')
    name = models.CharField(max_length=300, help_text='عنوان مدیا')
    source = models.FileField(upload_to='uploads/MediaFiles', help_text='فایل مدیا')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.name}'


class ClinicMedia(models.Model):
    media = models.ForeignKey(to=Media, related_name='clinicMedia_medias', on_delete=models.CASCADE, help_text='مدیا')
    clinic = models.ForeignKey(to=Clinic, related_name='clinicMedia_clinic', on_delete=models.CASCADE,
                               help_text='کلینیک')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.media.name} of {self.clinic.title}'


class ClinicInfo(models.Model):
    clinic = models.ForeignKey(to=Clinic, related_name='clinicInfos', on_delete=models.CASCADE, help_text='کلینیک')
    name = models.CharField(max_length=200, null=True, blank=True, help_text='عنوان باکس معرفی')
    icon = models.ImageField(upload_to='uploads/image/ClinicsIcon', null=True, blank=True, help_text='آیکون')
    showState = models.BooleanField(default=True, help_text='وضعیت نمایش')
    priority = models.IntegerField(default=0, help_text='اولویت نمایش')
    description = models.TextField(null=True, blank=True, help_text='توضیحات')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.name}'


class RealClinic(models.Model):
    name = models.CharField(max_length=200, help_text='نام کلینیک')
    description = models.TextField(blank=True, help_text='توضیحات')
    address = models.CharField(max_length=600, blank=True, help_text='آدرس کلینیک')
    icon = models.ImageField(upload_to='uploads/image/RealClinicsIcon', null=True, blank=True, help_text='آیکون')
    showState = models.BooleanField(default=True, help_text='وضعیت نمایش')
    priority = models.IntegerField(default=0, help_text='اولویت نمایش')
    long = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=6, help_text='مختصات عرض جغرافیایی')
    lat = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=6, help_text='مختصات طول جغرافیاییک')
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.icon:
            self.icon = STATIC_URL + 'Core/DefaultPics/clinic-default-icon.png'
        super(RealClinic, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


QUESTION_TYPE_CHOICES = (
    (1, "MULTIPLE_DATE"),
    (2, "NUMBER"),
    (3, "DATE"),
    (4, "CHART"),
    (5, "MULTIPLE_CHOICE"),
    (6, "PLACEHOLDER"),
    (7, "WEIGHT"),
    (8, "PICTURE")
)
EXPERT_LEVEL_CHOICES = (
    (1, "غیر اختصاصی"),
    (2, "نیمه اختصاصی"),
    (3, "اختصاصی")
)
PRIORITY_LEVEL_CHOICES = (
    (1, "سطح اولویت یک"),
    (2, "سطح اولویت دو"),
    (3, "سطح اولویت سه"),
    (4, "سطح اولویت چهار"),
    (5, "سطح اولویت پنج"),
)
DATE_TYPE_CHOICES = (
    (1, "سال"),
    (2, "ماه"),
    (3, "هفته"),
    (4, "روز")
)


class QuestionShare(models.Model):
    doctor = models.ForeignKey(to=Doctor, related_name='questionShares_doctor', on_delete=models.CASCADE,
                               help_text='پزشک طراح سوال')
    clinic = models.ForeignKey(to=Clinic, related_name='questionShares_clinic', on_delete=models.CASCADE,
                               help_text='کلینیک')
    # clinic_checkup = models.ForeignKey(to='ClinicCheckup', null=True, blank=True, related_name='questionShares_clinicCheckup',
    #                                    on_delete=models.CASCADE, help_text='چکاپ کلینیک')
    title = models.TextField(help_text='صورت سوال')
    short_title = models.CharField(max_length=300, help_text='عنوان کوتاه شده')
    expert_level = models.IntegerField(null=True, blank=True, choices=EXPERT_LEVEL_CHOICES, default=1)
    is_starter = models.BooleanField(default=False, help_text='اولین سوال برای شروع چکاپ')
    question_type = models.IntegerField(null=True, blank=True, choices=QUESTION_TYPE_CHOICES, default=1)
    prority_type = models.IntegerField(null=True, blank=True, choices=PRIORITY_LEVEL_CHOICES, default=1)
    is_date = models.BooleanField(default=False)
    is_date_limit = models.BooleanField(default=False)
    date_limit_num = models.FloatField(null=True, blank=True)
    date_type = models.IntegerField(null=True, blank=True, choices=DATE_TYPE_CHOICES, default=1)
    is_show_chart = models.BooleanField(default=False)
    is_equation = models.BooleanField(default=False)
    is_multiple_choice = models.BooleanField(default=False)
    equation = models.CharField(max_length=500, blank=True, help_text='معادله')
    chart_is_visible = models.BooleanField(default=False)
    chart_global_src_x = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات x مبدا در چارت')
    chart_global_src_y = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات y مبدا در چارت')
    chart_global_des_x = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات x مقصد در چارت')
    chart_global_des_y = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات y مقصد در چارت')
    chart_connectQstId = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                           help_text='سوال فرزند که به آن متصل است')
    chart_branchCount = models.SmallIntegerField(default=0, help_text='تعداد شاخه های سوال')

    # Expertise level

    def __str__(self):
        return f'{self.short_title}'


# class QuestionChart(models.Model):
#     questionShare = models.ForeignKey(to=QuestionShare, related_name='questionChart_questionShares', on_delete=models.CASCADE,
#                                help_text='')
#     is_starter = models.BooleanField(default=False, help_text='اولین سوال برای شروع چکاپ')
#     chart_is_visible = models.BooleanField(default=False)
#     chart_global_src_x = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات x مبدا در چارت')
#     chart_global_src_y = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات y مبدا در چارت')
#     chart_global_des_x = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات x مقصد در چارت')
#     chart_global_des_y = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات y مقصد در چارت')
#     chart_connectQstId = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
#                                            help_text='سوال فرزند که به آن متصل است')
#     chart_branchCount = models.SmallIntegerField(default=0, help_text='تعداد شاخه های سوال')
#
#     def __str__(self):
#         return f'{self.questionShare.title}'


class QuestionShareMedia(models.Model):
    media = models.ForeignKey(to=Media, related_name='QuestionShareMedia_medias', on_delete=models.CASCADE,
                              help_text='مدیا')
    questionShare = models.ForeignKey(to=QuestionShare, related_name='QuestionShareMedia_questionShares',
                                      on_delete=models.CASCADE, help_text='سوال مربوطه')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.media.name} of {self.questionShare.title}'


class QuestionOrgan(models.Model):
    organ = models.ForeignKey(to=Organ, related_name='questionOrgans_organ', on_delete=models.CASCADE,
                              help_text='عضو درگیر')
    questionShare = models.ForeignKey(to=QuestionShare, related_name='questionOrgans_questionShare',
                                      on_delete=models.CASCADE,
                                      help_text='سوال مرتبط')

    def __str__(self):
        return f'{self.organ.name} of {self.questionShare.short_title}'


class QuestionOption(models.Model):
    questionShare = models.ForeignKey(to=QuestionShare, related_name='questionOptions_questionShare',
                                      on_delete=models.CASCADE,
                                      help_text='سوال مرتبط')
    is_branch = models.BooleanField(default=False)
    title = models.CharField(max_length=500, blank=True, help_text='عنوان')
    weight = models.IntegerField(null=True, blank=True)
    interpretation = models.CharField(max_length=1000, blank=True, help_text='تفسیر این گزینه')
    alert = models.ForeignKey(to=Alert, null=True, blank=True, related_name='questionOptions_alert',
                              on_delete=models.CASCADE, help_text='هشدار این گزینه')
    tutorial = models.CharField(max_length=1000, blank=True, help_text='آموزش این گزینه')
    suggestedDoctor = models.ForeignKey(to=Doctor, null=True, blank=True, related_name='questionOptions_suggestedDoctor', on_delete=models.CASCADE, help_text='پزشک پیشنهادی')
    suggestedClinic = models.ForeignKey(to=Clinic, null=True, blank=True, related_name='questionOptions_suggestedClinic', on_delete=models.CASCADE, help_text='کلینیک پیشنهادی')
    chart_global_x = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات x در چارت')
    chart_global_y = models.FloatField(default=0.0, null=True, blank=True, help_text='مختصات y در چارت')
    chart_connectQstId = models.ForeignKey(QuestionShare, on_delete=models.SET_NULL, null=True, blank=True,
                                        help_text='سوال فرزند که به آن متصل است')

    def __str__(self):
        return f'{self.title} of {self.weight}'


class QuestionOptionDate(models.Model):
    questionOption = models.ForeignKey(to=QuestionOption, related_name='questionOptionDates', on_delete=models.CASCADE,
                                       help_text='سوال مرتبط')
    upper_band = models.FloatField(null=True, blank=True)
    lower_band = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.upper_band} - {self.lower_band}'


class QuestionOptionNumber(models.Model):
    questionOption = models.ForeignKey(to=QuestionOption, related_name='questionOptionNumbers',
                                       on_delete=models.CASCADE, help_text='سوال مرتبط')
    upper_band = models.FloatField(null=True, blank=True)
    lower_band = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.upper_band} - {self.lower_band}'


class QuestionOptionEquation(models.Model):
    questionOption = models.ForeignKey(to=QuestionOption, related_name='questionOptionEquations',
                                       on_delete=models.CASCADE, help_text='سوال مرتبط')
    upper_band = models.FloatField(null=True, blank=True)
    lower_band = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.upper_band} - {self.lower_band}'


class ClinicCheckup(models.Model):
    clinic = models.ForeignKey(to=Clinic, related_name='clinicCheckups_clinic', on_delete=models.CASCADE, help_text='کلینیک')
    title = models.CharField(max_length=200, help_text='عنوان چکاپ')
    required_time = models.PositiveSmallIntegerField(
        help_text='زمان مورد نیاز برای پاسخگویی به سوالات چکاپ بر حسب دقیقه')
    required_auth = models.BooleanField(default=False, help_text='نیازمند بودن چکاپ به احراز هویت')
    question_count = models.PositiveSmallIntegerField(help_text='تعداد سوالات چکاپ')
    approvers = models.CharField(max_length=400, blank=True, help_text='تایید کننده چکاپ')
    starting_question = models.ForeignKey(to=QuestionShare, related_name='clinicCheckups_questionShare',
                                          on_delete=models.CASCADE, help_text='کلینیک')
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} در کلینیک {self.clinic}'


class CheckupFlowchart(models.Model):
    text = models.TextField(help_text='متن فلوچارت در اپلیکیشن')
    title = models.CharField(max_length=100, help_text='نام فلوچارت')
    clinic_checkup = models.ForeignKey(to=ClinicCheckup, related_name='checkupFlowchart_ClinicCheckup',
                                       on_delete=models.CASCADE, help_text='چکاپ کلینیکی که این فلوچارت مربوط به آن است')

    def __str__(self):
        return f'{self.title} برای چکاپ کلینیک {self.clinic_checkup}'


class CheckupAnalyze(models.Model):
    text = models.TextField(help_text='متن آنالیز در اپلیکیشن')
    title = models.CharField(max_length=100, help_text='نام آنالیز')
    clinic_checkup = models.ForeignKey(to=ClinicCheckup, related_name='checkupAnalyze_ClinicCheckup',
                                       on_delete=models.CASCADE, help_text='چکاپ کلینیکی که این آنالیز مربوط به آن است')

    def __str__(self):
        return f'{self.title} برای چکاپ کلینیک {self.clinic_checkup}'


class Interpretation(models.Model):
    text = models.TextField(help_text='متن تفسیر')
    checkup_analyze = models.ForeignKey(to=CheckupAnalyze, related_name='interpretation_checkupAnalyze',
                                          on_delete=models.CASCADE, help_text='آنالیزی که این تفسیر متعلق به آن است')

    def __str__(self):
        return f'{self.text} برای فلوچارت {self.checkup_analyze}'


class Suggestion(models.Model):
    interpretation = models.ForeignKey(to=Interpretation, related_name='suggestion_interpretation',
                                       on_delete=models.CASCADE, help_text='تفسیری که این ارجاعات مربوط به آن است')
    alert = models.ForeignKey(to=Alert, null=True, blank=True, related_name='suggestion_alert',
                              on_delete=models.CASCADE, help_text='هشدار این گزینه')
    suggestedDoctor = models.ForeignKey(to=Doctor, null=True, blank=True, related_name='suggestion_suggestedDoctor',
                                        on_delete=models.CASCADE, help_text='پزشک مجازی پیشنهادی')
    suggestedClinic = models.ForeignKey(to=Clinic, null=True, blank=True, related_name='suggestion_suggestedClinic',
                                        on_delete=models.CASCADE, help_text='کلینیک مجازی پیشنهادی')
    suggestedRealDoctor = models.ForeignKey(to=RealDoctor, null=True, blank=True, related_name='suggestion_suggestedRealDoctor',
                                        on_delete=models.CASCADE, help_text='پزشک حقیقی پیشنهادی')
    suggestedRealClinic = models.ForeignKey(to=RealClinic, null=True, blank=True, related_name='suggestion_suggestedRealClinic',
                                        on_delete=models.CASCADE, help_text='کلینیک حقیقی پیشنهادی')
    suggestedMedia = models.ForeignKey(to=ClinicMedia, null=True, blank=True, related_name='suggestion_suggestedMedia',
                                        on_delete=models.CASCADE, help_text='آموزش پیشنهادی')

    def __str__(self):
        return f'{self.id} برای تفسیر {self.interpretation}'


class Checkup(models.Model):
    patientProfile = models.ForeignKey(to=PatientProfile, related_name='checkups_patientProfile',
                                       on_delete=models.CASCADE,
                                       help_text='پروفایل بیمار')
    clinic = models.ForeignKey(to=Clinic, related_name='checkups_clinic', on_delete=models.CASCADE, help_text='کلینیک')
    clinic_checkup = models.ForeignKey(to=ClinicCheckup, null=True, blank=True, related_name='checkups_clinicCheckup', on_delete=models.CASCADE,
                                       help_text='چکاپ کلینیک')
    title = models.CharField(max_length=250, null=True, blank=True, help_text='عنوان چکاپ')
    description = models.TextField(null=True, blank=True, help_text='توضیح چکاپ')
    executionDate = models.DateTimeField(auto_now=timezone.now())

    def save(self, *args, **kwargs):
        if self.clinic_checkup.required_auth is True and self.patientProfile.user.national_code_approval is False:
            raise SValidationError({"nationalCodeAuthentication": "چکاپ مورد نظر شما نیازمند احراز هویت میباشد، لطفا ابتدا احراز هویت کرده و سپس ادامه دهید"})
        else:
            if self.patientProfile.user.get_full_name():
                self.title = f' چکاپ {self.clinic_checkup.title} توسط {self.patientProfile.user.get_full_name()} در کلینیک {self.clinic.title} '
            else:
                self.title = f' چکاپ {self.clinic_checkup.title} توسط {self.patientProfile.user.phone_number} در کلینیک {self.clinic.title} '
        super(Checkup, self).save(*args, **kwargs)

    def __str__(self):
        if self.title:
            return f'{self.title}'
        else:
            return f' چکاپ {self.clinic_checkup.title} توسط {self.patientProfile.user.phone_number} در کلینیک {self.clinic.title} '


class QuestionAnswer(models.Model):
    checkup = models.ForeignKey(to=Checkup, related_name='questionAnswer_checkup', on_delete=models.CASCADE,
                                help_text='انتخاب چکاپ')
    questionShare = models.ForeignKey(to=QuestionShare, related_name='questionAnswer_questionShare',
                                      on_delete=models.CASCADE, help_text='انتخاب سوال')
    questionOption = models.ForeignKey(to=QuestionOption, related_name='questionAnswer_questionOption',
                                       on_delete=models.CASCADE, help_text='انتخاب جواب')


BLOOD_TYPE_CHOICES = (
    ('A+', "A+"),
    ('A-', "A-"),
    ('B+', "B+"),
    ('B-', "B-"),
    ('AB+', "AB+"),
    ('AB-', "AB-"),
    ('O+', "O+"),
    ('O-', "O-")
)

MARITAL_STATUS_CHOICES = (
    ('single', "مجرد"),
    ('married', "متاهل")
)

NATIONALITY_CHOICES = (
    ('iranian', "ایرانی"),
    ('non-iranian', "غیر ایرانی")
)

INSURANCE_TYPE_CHOICES = (
    (1, "تامین اجتماعی"),
    (2, "بیمه سلامت ایرانیان"),
    (3, "آزاد"),
)

EDUCATION_CHOICES = (
    ('illiterate', "بی سواد"),
    ('elementary', "ابتدایی"),
    ('middle', "سیکل"),
    ('diploma', "دیپلم"),
    ('associate', "کاردانی"),
    ('bachelor', "کارشناسی"),
    ('master', "کارشناسی ارشد"),
    ('doctoral', "دکتری"),
    ('postdoc', "فوق دکتری"),
)

FAMILY_MEMBER_CHOICES = (
    ('father', "پدر"),
    ('mother', "مادر"),
    ('sister', "خواهر"),
    ('brother', "برادر"),
    ('uncle-m', "دایی"),
    ('uncle-f', "عمو"),
    ('aunt-m', "خاله"),
    ('aunt-f', "عمه"),
    ('grandfather', "پدربزرگ"),
    ('grandmother', "مادربزرگ"),
    ('cousin-am', "پسرخاله، دخترخاله"),
    ('cousin-um', "پسردایی، دختردایی"),
    ('cousin-af', "پسرعمه، دخترعمه"),
    ('cousin-uf', "پسرعمو، دخترعمو"),
)


class Job(models.Model):
    title = models.CharField(max_length=200, help_text='نام شغل')

    def __str__(self):
        return self.title


class Illness(models.Model):
    title = models.CharField(max_length=200, help_text='نام بیماری')

    def __str__(self):
        return self.title


class Drug(models.Model):
    title = models.CharField(max_length=200, help_text='نام دارو')

    def __str__(self):
        return self.title


class DrugAmount(models.Model):
    title = models.CharField(max_length=200, help_text='مقدار استفاده')

    def __str__(self):
        return f'{self.title}'


class DrugInstruction(models.Model):
    title = models.CharField(max_length=200, help_text='دستور مصرف')

    def __str__(self):
        return f'{self.title}'


class PatientIllness(models.Model):
    illness = models.ForeignKey(Illness, on_delete=models.CASCADE,
                                related_name='patientIllness_illness', help_text='نام بیماری')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE,
                                   related_name='patientIllness_patient', help_text='کاربر')

    def __str__(self):
        return f"{self.patient.user}-{self.illness.title}"


class PatientFamilyIllness(models.Model):
    illness = models.ForeignKey(Illness, on_delete=models.CASCADE,
                                related_name='PatientFamilyIllness_illness', help_text='نام بیماری')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE,
                                   related_name='PatientFamilyIllness_patient', help_text='کاربر')
    family_member = models.CharField(max_length=11, choices=FAMILY_MEMBER_CHOICES,
                                     help_text='عضو خانوده ای که بیماری را دارد')


class PatientDrug(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE,
                                related_name='PatientDrug_patient', help_text='کاربر')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE,
                             related_name='PatientDrug_drug', help_text='نام دارو')
    amount = models.ForeignKey(DrugAmount, on_delete=models.CASCADE,
                               related_name='PatientDrug_amount', help_text='مقدار مصرف')
    instruction = models.ForeignKey(DrugInstruction, on_delete=models.CASCADE,
                                    related_name='PatientDrug_instruction', help_text='زمان مصرف')

    def __str__(self):
        return f"{self.patient.user}--{self.drug}"


class PatientJob(models.Model):
    job = models.ForeignKey(to=Job, related_name='patientJob_job',
                            on_delete=models.CASCADE, help_text='شغل')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE,
                                   related_name='patientJob_patient', help_text='کاربر')

    def __str__(self):
        return f"{self.patient.user}-{self.job.title}"


class PatientBiography(models.Model):
    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE,
                                   related_name='patientBiography_patient', help_text='کاربر')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, help_text='گروه خونی')
    birth_date = models.DateField(help_text='تاریخ تولد')
    landline = models.CharField(validators=[validate_landline], max_length=11, help_text='تلفن ثابت')
    marital_status = models.CharField(max_length=7, choices=MARITAL_STATUS_CHOICES, help_text='وضعیت تاهل')
    nationality = models.CharField(max_length=11, choices=NATIONALITY_CHOICES, help_text='ملیت')
    education = models.CharField(max_length=10, choices=EDUCATION_CHOICES, help_text='تحصیلات')
    insurance_type = models.IntegerField(choices=INSURANCE_TYPE_CHOICES, help_text='نوع بیمه')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def __str__(self):
        return f'{self.patient.user}'


class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE,
                                   related_name='medical_record_patient', help_text='کاربر')
    height = models.PositiveSmallIntegerField(help_text='قد بر حسب سانتی متر')
    weight = models.PositiveSmallIntegerField(help_text='وزن بر حسب کیلوگرم')
    bmi = models.DecimalField(max_digits=3, null=True, blank=True, decimal_places=1, help_text='نمایه توده بدنی')
    systolic_blood_pressure = models.PositiveSmallIntegerField(help_text='فشار خون سیستولیک')
    diastolic_blood_pressure = models.PositiveSmallIntegerField(help_text='فشار خون دیاستولیک')
    created_on = models.DateTimeField(auto_now=timezone.now())

    def save(self, *args, **kwargs):
        square_height = int(self.height) * int(self.height) / 10000
        self.bmi = int(self.weight) / square_height
        super(MedicalRecord, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.patient.user}'

# class QuestionDefultItem(models.Model):
#     question = models.ForeignKey(to=Question, related_name='questionDefultItems', on_delete=models.CASCADE, help_text='سوال')
#     value = models.CharField(max_length=500, help_text='مقدار')
#     priority = models.IntegerField(default=0, help_text='اولویت نمایش')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.value} of {self.question.title}'
#
#
# class Answer(models.Model):
#     question = models.ForeignKey(to=Question, related_name='answers', on_delete=models.CASCADE, help_text='سوال')
#     checkup = models.ForeignKey(to=Checkup, related_name='answers', on_delete=models.CASCADE, help_text='چکاپ')
#     value = models.CharField(max_length=500, help_text='پاسخ')
#     isValueTF = models.BooleanField(default=False, help_text='نوع پاسخ صحیح یا غلط')
#     valueTF = models.BooleanField(null=True, blank=True, help_text='پاسخ صحیح یا غلط')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.value} of {self.question.title}'
#
#
# class ClinicQuestion(models.Model):
#     question = models.ForeignKey(to=Question, related_name='clinicQuestions', on_delete=models.CASCADE, help_text='سوال')
#     clinic = models.ForeignKey(to=Clinic, related_name='clinicQuestions', on_delete=models.CASCADE, help_text='کلینیک')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.question.title} of {self.clinic.title}'
#
#
#
# class MMMQuestionInputType(models.Model):
#     title = models.CharField(max_length=500, help_text='ورود اطلاعات یا انتخاب از لیست')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.title}'
#
#
# class MMMQuestionFormatType(models.Model):
#     title = models.CharField(max_length=500, help_text='فرمت سوال مثل عدد، متن، تاریخ، ساعت و درست و غلط')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.title}'
#
#
# class MMMQuestionGroup(models.Model):
#     title = models.CharField(max_length=500, help_text='گروه بندی سوالات مثل عمومی و تخصصی، فاکنورهای آزمایشگاهی، دارویی و تغذیه')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.title}'
#
#
# class MMMQuestion(models.Model):
#     questionGroup = models.ForeignKey(to=QuestionGroup, related_name='questions', on_delete=models.CASCADE, help_text='گروه سوال')
#     questionType = models.ForeignKey(to=QuestionFormatType, related_name='questions', on_delete=models.CASCADE, help_text='فرمت سوال')
#     questionInputType = models.ForeignKey(to=QuestionInputType, related_name='questions', on_delete=models.CASCADE, help_text='نوع ورودی')
#     title = models.CharField(max_length=500, help_text='متن سوال')
#     inputMaskFormat = models.CharField(max_length=500, null=True, blank=True, help_text='ماسک فرمت ورودی')
#     betweenRanges = models.BooleanField(default=False, help_text='پرچم نوع رنج')
#     description = models.TextField(null=True, blank=True, help_text='توضیحات')
#     created_on = models.DateTimeField(auto_now=timezone.now())
#
#     def __str__(self):
#         return f'{self.title}'
