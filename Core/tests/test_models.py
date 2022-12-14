import pytest
from Core import models


@pytest.mark.django_db
class TestModels:
    @pytest.fixture
    def setup(self):
        self.user = models.User.objects.create_user(phone_number="09355555555")

    def test_user(self, setup):
        user = self.user
        assert str(user.phone_number) == '09355555555'

    def test_relative_type(self):
        relative_type = models.RelativeType.objects.create(title='فرزند')
        assert str(relative_type.title) == 'فرزند'

    def test_organ(self):
        organ = models.Organ.objects.create(name='مچ')
        assert str(organ.name) == 'مچ'

    def test_doctor(self, setup):
        user = self.user
        doctor = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        assert str(doctor.description) == 'متخصص'

    def test_clinic_group(self):
        clinic_group = models.ClinicGroup.objects.create(title='بیمارستان رجایی')
        assert str(clinic_group.title) == 'بیمارستان رجایی'

    def test_clinic(self, setup):
        user = self.user
        clinic_group = models.ClinicGroup.objects.create(title='بیمارستان رجایی')
        agent = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        clinic = models.Clinic.objects.create(
            clinicGroup=clinic_group,
            agent=agent,
            title='کلینیک دیابت'
        )
        assert str(clinic.title) == 'کلینیک دیابت'

    def test_alert(self):
        alert = models.Alert.objects.create(
            title='رمز نامعتبر',
            description='رمز کوتاه است'
        )
        assert str(alert.description) == 'رمز کوتاه است'

    def test_clinic_info(self, setup):
        user = self.user
        clinic_group = models.ClinicGroup.objects.create(title='بیمارستان رجایی')
        agent = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        clinic = models.Clinic.objects.create(
            clinicGroup=clinic_group,
            agent=agent,
            title='کلینیک دیابت'
        )
        clinic_info = models.ClinicInfo.objects.create(
            clinic=clinic,
            description='در این کلینیک تمام خدمات مربوط به دیابتی ها انجام میشود'
        )
        assert str(clinic_info.description) == 'در این کلینیک تمام خدمات مربوط به دیابتی ها انجام میشود'

    def test_checkup(self, setup):
        user = self.user
        clinic_group = models.ClinicGroup.objects.create(title='بیمارستان رجایی')
        agent = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        clinic = models.Clinic.objects.create(
            clinicGroup=clinic_group,
            agent=agent,
            title='کلینیک دیابت'
        )
        patient_profile = models.PatientProfile.objects.create(user=user)
        checkup = models.Checkup.objects.create(
            patientProfile=patient_profile,
            clinic=clinic
        )
        assert str(checkup.clinic.title) == 'کلینیک دیابت'

    def test_question_share(self, setup):
        user = self.user
        doctor = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        question_share = models.QuestionShare.objects.create(
            doctor=doctor,
            title='آیا شما مبتلا به دیابت هستید؟',
            short_title='برسی ابتلا به دیابت'
        )
        assert str(question_share.short_title) == 'برسی ابتلا به دیابت'

    def test_question_organ(self, setup):
        organ = models.Organ.objects.create(name='پانکراس')
        user = self.user
        doctor = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        question_share = models.QuestionShare.objects.create(
            doctor=doctor,
            title='آیا شما مبتلا به دیابت هستید؟',
            short_title='برسی ابتلا به دیابت'
        )
        question_organ = models.QuestionOrgan.objects.create(
            organ=organ,
            questionShare=question_share
        )
        assert str(question_organ.questionShare.short_title) == 'برسی ابتلا به دیابت'

    def test_question_option(self, setup):
        user = self.user
        doctor = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        question_share = models.QuestionShare.objects.create(
            doctor=doctor,
            title='آیا شما مبتلا به دیابت هستید؟',
            short_title='برسی ابتلا به دیابت'
        )
        clinic_group = models.ClinicGroup.objects.create(title='بیمارستان رجایی')
        agent = models.Doctor.objects.create(user=user, specialyTitle='دکتر قلب', description='متخصص')
        clinic = models.Clinic.objects.create(
            clinicGroup=clinic_group,
            agent=agent,
            title='کلینیک دیابت'
        )
        doctor = models.Doctor.objects.create(user=user, specialyTitle='دکتر داخلی', description='متخصص')
        question_option = models.QuestionOption.objects.create(
            questionShare=question_share,
            suggestedDoctor=doctor,
            suggestedClinic=clinic
        )
        assert str(question_option.suggestedDoctor.description) == 'متخصص'
