from rest_framework import routers
from . import views as myapp_views
from django.urls import path, include
from django.conf.urls import url

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Dr.Griffin API",
      default_version='v1',
      description="API of backend",
      terms_of_service="http://www.drgriffin.ir/",
      contact=openapi.Contact(email="contact@drgriffin.ir"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'clinicGroups', myapp_views.ClinicGroupViewset, basename='clinicGroups')
router.register(r'users', myapp_views.UserViewset, basename='users')
router.register(r'relativeTypes', myapp_views.RelativeTypeViewset, basename='relativeTypes')
router.register(r'patientProfiles', myapp_views.PatientProfileViewset, basename='patientProfiles')
router.register(r'supervisors', myapp_views.SupervisorViewset, basename='supervisors')
router.register(r'doctors', myapp_views.DoctorViewset, basename='doctors')
router.register(r'clinics', myapp_views.ClinicViewset, basename='clinics')
router.register(r'organs', myapp_views.OrganViewset, basename='organs')
router.register(r'questionOptionEquations', myapp_views.QuestionOptionEquationViewset, basename='questionOptionEquations')
router.register(r'questionOptionNumbers', myapp_views.QuestionOptionNumberViewset, basename='questionOptionNumbers')
router.register(r'questionOptionDates', myapp_views.QuestionOptionDateViewset, basename='questionOptionDates')
router.register(r'questionOrgans', myapp_views.QuestionOrganViewset, basename='questionOrgans')
router.register(r'questionOptions', myapp_views.QuestionOptionViewset, basename='questionOptions')
router.register(r'questionShares', myapp_views.QuestionShareViewset, basename='questionShares')
router.register(r'alerts', myapp_views.AlertsViewset, basename='alerts')
router.register(r'checkups', myapp_views.CheckupViewset, basename='checkups')
router.register(r'media', myapp_views.MediaViewset, basename='media')
router.register(r'clinicMedia', myapp_views.ClinicMediaViewset, basename='clinicMedia')
router.register(r'clinicCheckups', myapp_views.ClinicCheckupViewset, basename='clinicCheckup')
router.register(r'checkupFlowchart', myapp_views.CheckupFlowchartViewset, basename='checkupFlowchart')
router.register(r'checkupAnalyze', myapp_views.CheckupAnalyzeViewset, basename='checkupAnalyze')
router.register(r'interpretation', myapp_views.InterpretationViewset, basename='interpretation')
router.register(r'suggestion', myapp_views.SuggestionViewset, basename='suggestion')
router.register(r'job', myapp_views.JobViewset, basename='job')
router.register(r'illness', myapp_views.IllnessViewset, basename='illness')
router.register(r'drug', myapp_views.DrugViewset, basename='drug')
router.register(r'drugAmount', myapp_views.DrugAmountViewset, basename='drugAmount')
router.register(r'drugInstruction', myapp_views.DrugInstructionViewset, basename='drugInstruction')
router.register(r'patientIllness', myapp_views.PatientIllnessViewset, basename='patientIllness')
router.register(r'patientFamilyIllness', myapp_views.PatientFamilyIllnessViewset, basename='patientFamilyIllness')
router.register(r'patientDrug', myapp_views.PatientDrugViewset, basename='patientDrug')
router.register(r'patientJob', myapp_views.PatientJobViewset, basename='patientJob')
router.register(r'patientBiography', myapp_views.PatientBiographyViewset, basename='patientBiography')
router.register(r'medicalRecord', myapp_views.MedicalRecordViewset, basename='medicalRecord')
router.register(r'realClinic', myapp_views.RealClinicViewset, basename='realClinic')
router.register(r'realDoctor', myapp_views.RealDoctorViewset, basename='realDoctor')
router.register(r'questionAnswers', myapp_views.QuestionAnswerViewset, basename='questionAnswers')
# router.register(r'lightQuestionShares', myapp_views.LightQuestionShareViewset, basename='lightQuestionShares')
# router.register(r'lqo', myapp_views.LightQuestionOptionViewset, basename='lqo')
router.register(r'compressedQuestionShares', myapp_views.CompressedQuestionShareViewset, basename='compressedQuestionShares')
router.register(r'questionShareMedias', myapp_views.QuestionShareMediaViewset, basename='questionShareMedias')


urlpatterns = [
    path('', include(router.urls)),
    url(r'^flowchart$', myapp_views.FlowchartViewSet.as_view, name='flowchart'),
    url(r'^flowchart2$', myapp_views.flowchart, name='flowchart2'),
    url(r'^register$', myapp_views.create_auth, name='create_auth'),
    url(r'^search$', myapp_views.search, name='search'),
    url(r'^checkup_result$', myapp_views.checkup_result, name='checkup_result'),
    # url(r'^clinic-toturials$', myapp_views.clinic_search, name='clinic-toturials'),
    # path('flowchart2/', myapp_views.flowchart, name='flowchart2'),

    path('user/', include('user_panel.urls')),
    path('add-supervisor/', myapp_views.SupervisorAPIView.as_view(), name='add-supervisor'),
    path('verify-supervisor/', myapp_views.SupervisorRegisterAPIView.as_view(), name='verify-supervisor'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
