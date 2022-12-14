from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from Core import models
import pytest


@pytest.mark.django_db
class OrganTests(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_organ(self):
        """
        Ensure we can create a new Organ object.
        """

        url = reverse('organs-list')
        data = {'name': 'دست'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Organ.objects.count(), 1)
        self.assertEqual(models.Organ.objects.get().name, 'دست')

    def test_list_organ(self):
        """
        Ensure we can get Organ objects list.
        """

        url = reverse('organs-list')
        data = {'name': 'دست'}
        self.client.post(url, data, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Organ.objects.count(), 1)
        self.assertEqual(models.Organ.objects.first().name, 'دست')
        self.assertEqual(response.json().get('count'), 1)

    def test_update_organ(self):
        """
        Ensure we can update an Organ object.
        """

        url1 = reverse('organs-list')
        url2 = reverse('organs-detail', kwargs={'pk': 1})
        data1 = {'name': 'دست'}
        data2 = {'name': 'پا'}
        self.client.post(url1, data1, format='json')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Organ.objects.count(), 1)
        self.assertEqual(models.Organ.objects.first().name, 'پا')

    def test_retrieve_organ(self):
        """
        Ensure we can retrieve an Organ object.
        """

        url1 = reverse('organs-list')
        url2 = reverse('organs-detail', kwargs={'pk': 1})
        data1 = {'name': 'دست'}
        self.client.post(url1, data1, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Organ.objects.count(), 1)
        self.assertEqual(response.json().get('name'), 'دست')

    def test_partial_update_organ(self):
        """
         Ensure we can partial_update an Organ object.
        """

        url1 = reverse('organs-list')
        url2 = reverse('organs-detail', kwargs={'pk': 2})
        data1 = {'name': 'دست'}
        data2 = {'name': 'مچ', 'parent': 1}
        data3 = {'name': 'آرنج'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.patch(url2, data3, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Organ.objects.count(), 2)
        self.assertEqual(models.Organ.objects.last().name, 'آرنج')
        self.assertEqual(models.Organ.objects.last().parent, models.Organ.objects.first())

    def test_destroy_organ(self):
        """
         Ensure we can destroy an Organ object.
        """

        url1 = reverse('organs-list')
        url2 = reverse('organs-detail', kwargs={'pk': 2})
        data1 = {'name': 'دست'}
        data2 = {'name': 'آرنج'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.Organ.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.Organ.objects.count(), 1)


@pytest.mark.django_db
class AlertTests(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_alert(self):
        """
        Ensure we can create a new Alert object.
        """

        url = reverse('alerts-list')
        data = {'title': 'رمز نامعتبر', 'description': 'رمز کوتاه است'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Alert.objects.count(), 1)
        self.assertEqual(models.Alert.objects.get().title, 'رمز نامعتبر')

    def test_list_alert(self):
        """
        Ensure we can get Alert objects list.
        """

        url = reverse('alerts-list')
        data = {'title': 'رمز نامعتبر', 'description': 'رمز کوتاه است'}
        self.client.post(url, data, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Alert.objects.count(), 1)
        self.assertEqual(models.Alert.objects.first().title, 'رمز نامعتبر')
        self.assertEqual(response.json().get('count'), 1)

    def test_update_alert(self):
        """
        Ensure we can update an Alert object.
        """

        url1 = reverse('alerts-list')
        url2 = reverse('alerts-detail', kwargs={'pk': 1})
        data1 = {'title': 'رمز نامعتبر', 'description': 'رمز کوتاه است'}
        data2 = {'title': 'تکمیل مدارک', 'description': 'عکس کارت ملی را آپلود کنید'}
        self.client.post(url1, data1, format='json')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Alert.objects.count(), 1)
        self.assertEqual(models.Alert.objects.first().title, 'تکمیل مدارک')

    def test_retrieve_alert(self):
        """
        Ensure we can retrieve an Alert object.
        """

        url1 = reverse('alerts-list')
        url2 = reverse('alerts-detail', kwargs={'pk': 1})
        data1 = {'title': 'رمز نامعتبر', 'description': 'رمز کوتاه است'}
        self.client.post(url1, data1, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Alert.objects.count(), 1)
        self.assertEqual(response.json().get('title'), 'رمز نامعتبر')

    def test_partial_update_alert(self):
        """
         Ensure we can partial_update an Alert object.
        """

        url1 = reverse('alerts-list')
        url2 = reverse('alerts-detail', kwargs={'pk': 1})
        data1 = {'title': 'رمز نامعتبر', 'description': 'رمز کوتاه است'}
        data2 = {'title': 'رمز نادرست'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Alert.objects.count(), 1)
        self.assertEqual(models.Alert.objects.last().title, 'رمز نادرست')
        self.assertEqual(models.Alert.objects.last().description, 'رمز کوتاه است')

    def test_destroy_alert(self):
        """
         Ensure we can destroy an Alert object.
        """

        url1 = reverse('alerts-list')
        url2 = reverse('alerts-detail', kwargs={'pk': 2})
        data1 = {'title': 'رمز نامعتبر', 'description': 'رمز کوتاه است'}
        data2 = {'title': 'تکمیل مدارک', 'description': 'عکس کارت ملی را آپلود کنید'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.Alert.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.Alert.objects.count(), 1)


@pytest.mark.django_db
class RelativeType(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_rt(self):
        """
        Ensure we can create a new RelativeType object.
        """

        url = reverse('relativeTypes-list')
        data = {'title': 'پدر'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.RelativeType.objects.count(), 1)
        self.assertEqual(models.RelativeType.objects.get().title, 'پدر')

    def test_list_rt(self):
        """
        Ensure we can get RelativeType objects list.
        """

        url = reverse('relativeTypes-list')
        data1 = {'title': 'پدر'}
        data2 = {'title': 'پسر'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.RelativeType.objects.count(), 2)
        self.assertEqual(models.RelativeType.objects.last().title, 'پسر')
        self.assertEqual(models.RelativeType.objects.first().title, 'پدر')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_rt(self):
        """
        Ensure we can update a RelativeType object.
        """

        url1 = reverse('relativeTypes-list')
        url2 = reverse('relativeTypes-detail', kwargs={'pk': 1})
        data1 = {'title': 'پدر'}
        data2 = {'title': 'پسر'}
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.RelativeType.objects.first().title, 'پدر')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.RelativeType.objects.count(), 1)
        self.assertEqual(models.RelativeType.objects.first().title, 'پسر')

    def test_retrieve_rt(self):
        """
        Ensure we can retrieve a RelativeType object.
        """

        url1 = reverse('relativeTypes-list')
        url2 = reverse('relativeTypes-detail', kwargs={'pk': 2})
        data1 = {'title': 'پدر'}
        data2 = {'title': 'پسر'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.RelativeType.objects.count(), 2)
        self.assertEqual(response.json().get('title'), 'پسر')

    def test_partial_update_rt(self):
        """
         Ensure we can partial_update a RelativeType object.
        """

        url1 = reverse('relativeTypes-list')
        url2 = reverse('relativeTypes-detail', kwargs={'pk': 1})
        data1 = {'title': 'پدر'}
        data2 = {'title': 'پسر'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.RelativeType.objects.count(), 1)
        self.assertEqual(models.RelativeType.objects.last().title, 'پسر')

    def test_destroy_rt(self):
        """
         Ensure we can destroy a RelativeType object.
        """

        url1 = reverse('relativeTypes-list')
        url2 = reverse('relativeTypes-detail', kwargs={'pk': 2})
        data1 = {'title': 'پدر'}
        data2 = {'title': 'پسر'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.RelativeType.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.RelativeType.objects.count(), 1)


@pytest.mark.django_db
class Doctor(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_doctor(self):
        """
        Ensure we can create a new Doctor object.
        """

        url = reverse('doctors-list')
        data = {'user': '1', 'systemCode': '12345', 'description': 'دکتر متخصص قلب'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Doctor.objects.count(), 1)
        self.assertEqual(models.Doctor.objects.get().systemCode, '12345')

    def test_list_doctor(self):
        """
        Ensure we can get Doctor objects list.
        """

        url = reverse('doctors-list')
        data1 = {'user': '1', 'systemCode': '12345', 'description': 'دکتر متخصص قلب'}
        data2 = {'user': '1', 'systemCode': '123456', 'description': 'دکتر متخصص مغز و اعصاب'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Doctor.objects.count(), 2)
        self.assertEqual(models.Doctor.objects.last().description, 'دکتر متخصص مغز و اعصاب')
        self.assertEqual(models.Doctor.objects.first().description, 'دکتر متخصص قلب')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_doctor(self):
        """
        Ensure we can update a Doctor object.
        """

        url1 = reverse('doctors-list')
        url2 = reverse('doctors-detail', kwargs={'pk': 1})
        data1 = {'user': '1', 'systemCode': '12345', 'description': 'دکتر متخصص قلب'}
        data2 = {'user': '1', 'systemCode': '123456', 'description': 'دکتر متخصص مغز و اعصاب'}
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.Doctor.objects.first().description, 'دکتر متخصص قلب')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Doctor.objects.count(), 1)
        self.assertEqual(models.Doctor.objects.first().description, 'دکتر متخصص مغز و اعصاب')

    def test_retrieve_doctor(self):
        """
        Ensure we can retrieve a Doctor object.
        """

        url1 = reverse('doctors-list')
        url2 = reverse('doctors-detail', kwargs={'pk': 2})
        data1 = {'user': '1', 'systemCode': '12345', 'description': 'دکتر متخصص قلب'}
        data2 = {'user': '1', 'systemCode': '123456', 'description': 'دکتر متخصص مغز و اعصاب'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Doctor.objects.count(), 2)
        self.assertEqual(response.json().get('description'), 'دکتر متخصص مغز و اعصاب')

    def test_partial_update_doctor(self):
        """
         Ensure we can partial_update a Doctor object.
        """

        url1 = reverse('doctors-list')
        url2 = reverse('doctors-detail', kwargs={'pk': 1})
        data1 = {'user': '1', 'systemCode': '12345', 'description': 'دکتر متخصص قلب'}
        data2 = {'description': 'دکتر متخصص مغز و اعصاب'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Doctor.objects.count(), 1)
        self.assertEqual(models.Doctor.objects.last().description, 'دکتر متخصص مغز و اعصاب')

    def test_destroy_doctor(self):
        """
         Ensure we can destroy a Doctor object.
        """

        url1 = reverse('doctors-list')
        url2 = reverse('doctors-detail', kwargs={'pk': 2})
        data1 = {'user': '1', 'systemCode': '12345', 'description': 'دکتر متخصص قلب'}
        data2 = {'user': '1', 'systemCode': '123456', 'description': 'دکتر متخصص مغز و اعصاب'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.Doctor.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.Doctor.objects.count(), 1)


@pytest.mark.django_db
class ClinicGroup(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_cg(self):
        """
        Ensure we can create a new ClinicGroup object.
        """

        url = reverse('clinicGroups-list')
        data = {'title': 'کلینیک دیابت'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.ClinicGroup.objects.count(), 1)
        self.assertEqual(models.ClinicGroup.objects.get().title, 'کلینیک دیابت')

    def test_list_cg(self):
        """
        Ensure we can get ClinicGroup objects list.
        """

        url = reverse('clinicGroups-list')
        data1 = {'title': 'کلینیک دیابت'}
        data2 = {'title': 'کلینیک دندانپزشکی'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.ClinicGroup.objects.count(), 2)
        self.assertEqual(models.ClinicGroup.objects.first().title, 'کلینیک دیابت')
        self.assertEqual(models.ClinicGroup.objects.last().title, 'کلینیک دندانپزشکی')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_cg(self):
        """
        Ensure we can update a ClinicGroup object.
        """

        url1 = reverse('clinicGroups-list')
        url2 = reverse('clinicGroups-detail', kwargs={'pk': 1})
        data1 = {'title': 'کلینیک دیابت'}
        data2 = {'title': 'کلینیک دندانپزشکی'}
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.ClinicGroup.objects.first().title, 'کلینیک دیابت')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.ClinicGroup.objects.count(), 1)
        self.assertEqual(models.ClinicGroup.objects.first().title, 'کلینیک دندانپزشکی')

    def test_retrieve_cg(self):
        """
        Ensure we can retrieve a ClinicGroup object.
        """

        url1 = reverse('clinicGroups-list')
        url2 = reverse('clinicGroups-detail', kwargs={'pk': 2})
        data1 = {'title': 'کلینیک دیابت'}
        data2 = {'title': 'کلینیک دندانپزشکی'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.ClinicGroup.objects.count(), 2)
        self.assertEqual(response.json().get('title'), 'کلینیک دندانپزشکی')

    def test_partial_update_cg(self):
        """
         Ensure we can partial_update a ClinicGroup object.
        """

        url1 = reverse('clinicGroups-list')
        url2 = reverse('clinicGroups-detail', kwargs={'pk': 1})
        data1 = {'title': 'کلینیک دیابت'}
        data2 = {'title': 'کلینیک دندانپزشکی'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.ClinicGroup.objects.count(), 1)
        self.assertEqual(models.ClinicGroup.objects.last().title, 'کلینیک دندانپزشکی')

    def test_destroy_cg(self):
        """
         Ensure we can destroy a ClinicGroup object.
        """

        url1 = reverse('clinicGroups-list')
        url2 = reverse('clinicGroups-detail', kwargs={'pk': 2})
        data1 = {'title': 'کلینیک دیابت'}
        data2 = {'title': 'کلینیک دندانپزشکی'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.ClinicGroup.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.ClinicGroup.objects.count(), 1)


@pytest.mark.django_db
class Clinic(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.doctor = models.Doctor.objects.create(user=self.user)
        self.clinicGroup = models.ClinicGroup.objects.create(title='دکتر قلب')

    def test_create_clinic(self):
        """
        Ensure we can create a new Clinic object.
        """

        url = reverse('clinics-list')
        data = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید رجایی'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Clinic.objects.count(), 1)
        self.assertEqual(models.Clinic.objects.get().title, 'شهید رجایی')

    def test_list_clinic(self):
        """
        Ensure we can get Clinic objects list.
        """

        url = reverse('clinics-list')
        data1 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید رجایی'}
        data2 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید باهنر'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Clinic.objects.count(), 2)
        self.assertEqual(models.Clinic.objects.first().title, 'شهید رجایی')
        self.assertEqual(models.Clinic.objects.last().title, 'شهید باهنر')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_clinic(self):
        """
        Ensure we can update a Clinic object.
        """

        url1 = reverse('clinics-list')
        url2 = reverse('clinics-detail', kwargs={'pk': 1})
        data1 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید رجایی'}
        data2 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید باهنر'}
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.Clinic.objects.first().title, 'شهید رجایی')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Clinic.objects.count(), 1)
        self.assertEqual(models.Clinic.objects.first().title, 'شهید باهنر')

    def test_retrieve_clinic(self):
        """
        Ensure we can retrieve a Clinic object.
        """

        url1 = reverse('clinics-list')
        url2 = reverse('clinics-detail', kwargs={'pk': 2})
        data1 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید رجایی'}
        data2 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید باهنر'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Clinic.objects.count(), 2)
        self.assertEqual(response.json().get('title'), 'شهید باهنر')

    def test_partial_update_clinic(self):
        """
         Ensure we can partial_update a Clinic object.
        """

        url1 = reverse('clinics-list')
        url2 = reverse('clinics-detail', kwargs={'pk': 1})
        data1 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید رجایی'}
        data2 = {'title': 'شهید باهنر'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Clinic.objects.count(), 1)
        self.assertEqual(models.Clinic.objects.last().title, 'شهید باهنر')

    def test_destroy_clinic(self):
        """
         Ensure we can destroy a Clinic object.
        """

        url1 = reverse('clinics-list')
        url2 = reverse('clinics-detail', kwargs={'pk': 2})
        data1 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید رجایی'}
        data2 = {'clinicGroup': '1', 'agent': '1', 'title': 'شهید باهنر'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.Clinic.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.Clinic.objects.count(), 1)


@pytest.mark.django_db
class QuestionShare(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.doctor = models.Doctor.objects.create(user=self.user)

    def test_create_qs(self):
        """
        Ensure we can create a new QuestionShare object.
        """

        url = reverse('questionShares-list')
        data = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.QuestionShare.objects.count(), 1)
        self.assertEqual(models.QuestionShare.objects.get().title, 'سوال')

    def test_list_qs(self):
        """
        Ensure we can get QuestionShare objects list.
        """

        url = reverse('questionShares-list')
        data1 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال'}
        data2 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال2'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionShare.objects.count(), 2)
        self.assertEqual(models.QuestionShare.objects.first().title, 'سوال')
        self.assertEqual(models.QuestionShare.objects.last().title, 'سوال2')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_qs(self):
        """
        Ensure we can update a QuestionShare object.
        """

        url1 = reverse('questionShares-list')
        url2 = reverse('questionShares-detail', kwargs={'pk': 1})
        data1 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال'}
        data2 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال2'}
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.QuestionShare.objects.first().title, 'سوال')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionShare.objects.count(), 1)
        self.assertEqual(models.QuestionShare.objects.first().title, 'سوال2')

    def test_retrieve_qs(self):
        """
        Ensure we can retrieve a QuestionShare object.
        """

        url1 = reverse('questionShares-list')
        url2 = reverse('questionShares-detail', kwargs={'pk': 2})
        data1 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال'}
        data2 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال2'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionShare.objects.count(), 2)
        self.assertEqual(response.json().get('title'), 'سوال2')

    def test_partial_update_qs(self):
        """
         Ensure we can partial_update a QuestionShare object.
        """

        url1 = reverse('questionShares-list')
        url2 = reverse('questionShares-detail', kwargs={'pk': 1})
        data1 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال'}
        data2 = {'title': 'سوال2'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionShare.objects.count(), 1)
        self.assertEqual(models.QuestionShare.objects.last().title, 'سوال2')

    def test_destroy_qs(self):
        """
         Ensure we can destroy a QuestionShare object.
        """

        url1 = reverse('questionShares-list')
        url2 = reverse('questionShares-detail', kwargs={'pk': 2})
        data1 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال'}
        data2 = {'doctor': '1', 'questionOrgans': [], 'questionOptions': [], 'title': 'سوال2'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.QuestionShare.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.QuestionShare.objects.count(), 1)


@pytest.mark.django_db
class QuestionOrgan(APITestCase):

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.doctor = models.Doctor.objects.create(user=self.user)
        models.QuestionShare.objects.create(doctor=self.doctor, title='سوال')
        models.Organ.objects.create(name='دست')
        models.Organ.objects.create(name='سر')

    def test_create_qor(self):
        """
        Ensure we can create a new QuestionOrgan object.
        """

        url = reverse('questionOrgans-list')
        data = {'organ': '1', 'questionShare': '1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.QuestionOrgan.objects.count(), 1)
        self.assertEqual(models.QuestionOrgan.objects.get().organ.name, 'دست')

    def test_list_qor(self):
        """
        Ensure we can get QuestionOrgan objects list.
        """

        url = reverse('questionOrgans-list')
        data1 = {'organ': '1', 'questionShare': '1'}
        data2 = {'organ': '2', 'questionShare': '1'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOrgan.objects.count(), 2)
        self.assertEqual(models.QuestionOrgan.objects.first().organ.name, 'دست')
        self.assertEqual(models.QuestionOrgan.objects.last().organ.name, 'سر')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_qor(self):
        """
        Ensure we can update a QuestionOrgan object.
        """

        url1 = reverse('questionOrgans-list')
        url2 = reverse('questionOrgans-detail', kwargs={'pk': 1})
        data1 = {'organ': '1', 'questionShare': '1'}
        data2 = {'organ': '2', 'questionShare': '1'}
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.QuestionOrgan.objects.first().organ.name, 'دست')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOrgan.objects.count(), 1)
        self.assertEqual(models.QuestionOrgan.objects.first().organ.name, 'سر')

    def test_retrieve_qor(self):
        """
        Ensure we can retrieve a QuestionOrgan object.
        """

        url1 = reverse('questionOrgans-list')
        url2 = reverse('questionOrgans-detail', kwargs={'pk': 2})
        data1 = {'organ': '1', 'questionShare': '1'}
        data2 = {'organ': '2', 'questionShare': '1'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOrgan.objects.count(), 2)
        self.assertEqual(response.json().get('organ'), 2)

    def test_partial_update_qor(self):
        """
         Ensure we can partial_update a QuestionOrgan object.
        """

        url1 = reverse('questionOrgans-list')
        url2 = reverse('questionOrgans-detail', kwargs={'pk': 1})
        data1 = {'organ': '1', 'questionShare': '1'}
        data2 = {'organ': '2'}
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOrgan.objects.count(), 1)
        self.assertEqual(models.QuestionOrgan.objects.last().organ.name, 'سر')

    def test_destroy_qor(self):
        """
         Ensure we can destroy a QuestionOrgan object.
        """

        url1 = reverse('questionOrgans-list')
        url2 = reverse('questionOrgans-detail', kwargs={'pk': 2})
        data1 = {'organ': '1', 'questionShare': '1'}
        data2 = {'organ': '2', 'questionShare': '1'}
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.QuestionOrgan.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.QuestionOrgan.objects.count(), 1)


@pytest.mark.django_db
class QuestionOption(APITestCase):
    """
    In this test, we'll also test creating questionOptionEquations, questionOptionNumbers & questionOptionDates.
    """

    def setUp(self):
        self.user = models.User.objects.create_superuser(phone_number="09355555555", password='123123123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.doctor = models.Doctor.objects.create(user=self.user)
        models.QuestionShare.objects.create(doctor=self.doctor, title='سوال')

    def test_create_qop(self):
        """
        Ensure we can create a new QuestionOption object.
        """

        url = reverse('questionOptions-list')
        data = {
            'title': 'متن1',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.QuestionOption.objects.count(), 1)
        self.assertEqual(models.QuestionOption.objects.get().title, 'متن1')

    def test_list_qop(self):
        """
        Ensure we can get QuestionOption objects list.
        """

        url = reverse('questionOptions-list')
        data1 = {
            'title': 'متن1',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        data2 = {
            'title': 'متن2',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOption.objects.count(), 2)
        self.assertEqual(models.QuestionOption.objects.first().title, 'متن1')
        self.assertEqual(models.QuestionOption.objects.last().title, 'متن2')
        self.assertEqual(response.json().get('count'), 2)

    def test_update_qop(self):
        """
        Ensure we can update a QuestionOption object.
        """

        url1 = reverse('questionOptions-list')
        url2 = reverse('questionOptions-detail', kwargs={'pk': 1})
        data1 = {
            'title': 'متن1',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        data2 = {
            'title': 'متن2',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        self.client.post(url1, data1, format='json')
        self.assertEqual(models.QuestionOption.objects.first().title, 'متن1')
        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOption.objects.count(), 1)
        self.assertEqual(models.QuestionOption.objects.first().title, 'متن2')

    def test_retrieve_qop(self):
        """
        Ensure we can retrieve a QuestionOption object.
        """

        url1 = reverse('questionOptions-list')
        url2 = reverse('questionOptions-detail', kwargs={'pk': 2})
        data1 = {
            'title': 'متن1',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        data2 = {
            'title': 'متن2',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOption.objects.count(), 2)
        self.assertEqual(response.json().get('title'), 'متن2')

    def test_partial_update_qop(self):
        """
         Ensure we can partial_update a QuestionOption object.
        """

        url1 = reverse('questionOptions-list')
        url2 = reverse('questionOptions-detail', kwargs={'pk': 1})
        data1 = {
            'title': 'متن1',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        data2 = {
            'title': 'متن2',
        }
        self.client.post(url1, data1, format='json')
        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.QuestionOption.objects.count(), 1)
        self.assertEqual(models.QuestionOption.objects.last().title, 'متن2')

    def test_destroy_qop(self):
        """
         Ensure we can destroy a QuestionOption object.
        """

        url1 = reverse('questionOptions-list')
        url2 = reverse('questionOptions-detail', kwargs={'pk': 2})
        data1 = {
            'title': 'متن1',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        data2 = {
            'title': 'متن2',
            'questionShare': '1',
            'questionOptionEquations': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionNumbers': [{
                'upper_band': '2',
                'lower_band': '1'
            }],
            'questionOptionDates': [{
                'upper_band': '2',
                'lower_band': '1'
            }]
        }
        self.client.post(url1, data1, format='json')
        self.client.post(url1, data2, format='json')
        self.assertEqual(models.QuestionOption.objects.count(), 2)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.QuestionOption.objects.count(), 1)
