import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CheckupServer.settings')
django.setup()

from Core import models


def add_alert():
    obj_alert, c = models.Alert.objects.get_or_create(title="sample alert", description="description of alert")
    obj_alert, c = models.Alert.objects.get_or_create(title="sample alert1", description="description of alert1")
    obj_alert, c = models.Alert.objects.get_or_create(title="sample alert2", description="description of alert2")


def add_doctor():
    user = models.User.objects.all().first()
    obj_doctor, c = models.Doctor.objects.get_or_create(user=user, specialyTitle="Dr.", systemCode="1234")


def add_question_share():
    user = models.User.objects.all().last()
    doctor = models.Doctor.objects.get(user=user)
    clinic = models.Clinic.objects.get(agent=doctor)
    organ = models.Organ.objects.get(name='دست')
    title = 'آیا دست شما درد میکند؟'
    short_title = 'درد دست'
    obj_question_share, c = models.QuestionShare.objects.get_or_create(
        clinic=clinic, doctor=doctor, title=title, short_title=short_title)
    obj_question_organ, c = obj_question_share.questionOrgans_questionShare.get_or_create(
        questionShare=obj_question_share, organ=organ)
    obj_question_option, c = obj_question_share.questionOptions_questionShare.get_or_create(
        questionShare=obj_question_share, is_branch=True, title='بله', interpretation='سریعا به پزشک مراجعه کنید')
    obj_question_option, c = obj_question_share.questionOptions_questionShare.get_or_create(
            questionShare=obj_question_share, is_branch=True, title='خیر', interpretation='مشکلی ندارید')


def add_question_share2():

    info = {'phone_number': '09355555555', 'password': '123'}
    response = requests.post('http://127.0.0.1:8000/api/token/', data=info)

    tok = response.json()['access']

    my_headers = {'Authorization': f'Bearer {tok}'}

    url = 'http://127.0.0.1:8000/api/v1/questionShares/'
    data = {
        "short_title": "Question sample short title 5",
        "title": "long title of questions 5",
        "doctor": "1",
        "clinic": "1",
        "questionOrgans_questionShare": [{
            "organ": "1"
        },
        ],
        "questionOptions_questionShare": [{
            "title": "option qst 1",
            "questionOptionEquations": [],
            "questionOptionNumbers": [{
                "upper_band": "2",
                "lower_band": "6"
            },
                ],
            "questionOptionDates": []
        }
        ]
    }
    req = requests.post(url=url, data=data, headers=my_headers)
    print(f"{req}")


def get_drug_instruction():

    base_url = 'https://ep-test.tamin.ir/api/'
    headers = {'Context-Type': 'application/x-www-form-urlencoded'}

    response = requests.get(url=f'{base_url}ws-drug-instruction', headers=headers)
    jresponse = response.json()
    datas = jresponse['data']['list']
    for data in datas:
        models.DrugInstruction.objects.create(title=data['drugInstConcept'])


def get_drug_amount():

    base_url = 'https://ep-test.tamin.ir/api/'
    headers = {'Context-Type': 'application/x-www-form-urlencoded'}

    response = requests.get(url=f'{base_url}ws-drug-amount', headers=headers)
    jresponse = response.json()
    datas = jresponse['data']['list']
    for data in datas:
        models.DrugAmount.objects.create(title=data['drugAmntConcept'])

# get_drug_amount()
# get_drug_instruction()


def chechups_delete():
    checkups = models.Checkup.objects.all()
    for checkup in checkups:
        checkup.title = "test"
        checkup.save()

# chechups_delete()
