from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Clinic, Checkup, ClinicGroup, QuestionOption, QuestionOptionDate, QuestionOptionEquation, \
    MediaType, Media, RelativeType, ClinicMedia, QuestionOptionNumber, QuestionOrgan, QuestionShare, \
    ClinicInfo, PatientProfile, Doctor, Supervisor, Organ, Alert, User, QuestionShareMedia, QuestionAnswer, \
    MediaCategory, MedicalRecord, PatientBiography, Job, Illness, PatientIllness, PatientJob, PatientFamilyIllness, \
    Drug, DrugInstruction, DrugAmount, PatientDrug, ClinicCheckup, CheckupFlowchart, Interpretation, Suggestion, \
    RealClinic, RealDoctor, CheckupAnalyze


admin.site.register(Organ, DraggableMPTTAdmin)
admin.site.register([QuestionOptionDate, QuestionOptionEquation, QuestionOptionNumber, QuestionOrgan])
admin.site.register(Job)
admin.site.register(Illness)
admin.site.register(PatientIllness)
admin.site.register(PatientJob)
admin.site.register(Drug)
admin.site.register(DrugInstruction)
admin.site.register(DrugAmount)
admin.site.register(CheckupFlowchart)
admin.site.register(CheckupAnalyze)
admin.site.register(Interpretation)
admin.site.register(Suggestion)

# @admin.register(Person)
# class PersonAdmin(admin.ModelAdmin):
#     list_display = ("user", "name", "nationalCode")
#     # list_filter = ("",)
#     search_fields = ('user', "name", "nationalCode")
#     ordering = ('user',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "first_name", "last_name", "email", "national_code")
    list_filter = ("date_joined",)
    search_fields = ('phone_number',)
    ordering = ('phone_number',)


@admin.register(RelativeType)
class RelativeTypeAdmin(admin.ModelAdmin):
    list_display = ("title", "created_on")
    list_filter = ("created_on",)
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "questionShare", "title")
    list_filter = ("questionShare",)
    search_fields = ('title',)
    # ordering = ('title',)


@admin.register(QuestionShare)
class QuestionShareAdmin(admin.ModelAdmin):
    list_display = ("title", "short_title", "clinic", "is_starter")
    list_filter = ("clinic",)
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_on")
    list_filter = ("created_on",)
    search_fields = ('user',)
    ordering = ('user',)


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("user", "relativeType", "patient")
    list_filter = ("relativeType", "patient")
    search_fields = ('user', "patient")
    ordering = ('user',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "systemCode", "specialyTitle", "description")
    # list_filter = ("",)
    search_fields = ('user', "systemCode")
    ordering = ('user',)


admin.site.register(ClinicGroup)
# @admin.register(ClinicGroup)
# class ClinicGroupAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_on")
#     list_filter = ("created_on",)
#     search_fields = ('title',)
#     ordering = ('title',)


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("title", "agent", "created_on", "description")
    list_filter = ("created_on",)
    search_fields = ('title', 'agent',)
    ordering = ('-created_on',)


@admin.register(MediaType)
class MediaTypeAdmin(admin.ModelAdmin):
    list_display = ("title", "created_on")
    list_filter = ("created_on",)
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "category", "created_on")
    list_filter = ("created_on", "type", "category",)
    search_fields = ('name',)
    ordering = ('-created_on',)


@admin.register(ClinicMedia)
class ClinicMediaAdmin(admin.ModelAdmin):
    list_display = ("clinic", "media", "media_type", "media_category", "created_on")
    list_filter = ("created_on", "clinic",)
    search_fields = ('media',)
    ordering = ('media',)

    def media_category(self, obj):
        return obj.media.category

    def media_type(self, obj):
        return obj.media.type


@admin.register(QuestionShareMedia)
class QuestionShareMediaAdmin(admin.ModelAdmin):
    list_display = ("questionShare", "media", "media_type", "media_category", "created_on")
    list_filter = ("created_on", "questionShare",)
    search_fields = ('media', 'questionShare')
    ordering = ('media',)

    def media_category(self, obj):
        return obj.media.category

    def media_type(self, obj):
        return obj.media.type


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    # list_display = ("checkup", "questionShare", "questionOption", )
    list_display = ("id", "checkup_title", )
    # list_filter = ("checkup", "questionShare", "questionOption",)
    # search_fields = ('checkup',)

    def checkup_title(self, obj):
        if obj.checkup.title:
            return obj.checkup.title
        else:
            return ""


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "height", "weight", "bmi", "systolic_blood_pressure",
                    "diastolic_blood_pressure", "created_on", )
    list_filter = ("patient",)
    # search_fields = ['patient']
    ordering = ("-created_on",)


    # def checkup_title(self, obj):
    #     if obj.checkup.title:
    #         return obj.checkup.title
    #     else:
    #         return ""


@admin.register(PatientBiography)
class PatientBiographyAdmin(admin.ModelAdmin):
    list_display = ("patient", "blood_type", "birth_date", "landline", "marital_status",
                    "nationality", "education", "insurance_type", )
    # list_filter = ("checkup", "questionShare", "questionOption",)
    # search_fields = ('checkup',)

    # def checkup_title(self, obj):
    #     if obj.checkup.title:
    #         return obj.checkup.title
    #     else:
    #         return ""


@admin.register(ClinicCheckup)
class ClinicCheckupAdmin(admin.ModelAdmin):
    list_display = ("clinic", "title", "required_time", "question_count", "approvers", "starting_question", "required_auth" )
    # list_filter = ("checkup", "questionShare", "questionOption",)
    # search_fields = ('checkup',)

    # def checkup_title(self, obj):
    #     if obj.checkup.title:
    #         return obj.checkup.title
    #     else:
    #         return ""


@admin.register(PatientFamilyIllness)
class PatientFamilyIllnessAdmin(admin.ModelAdmin):
    list_display = ("patient", "family_member", "illness", )
    # list_filter = ("checkup", "questionShare", "questionOption",)
    # search_fields = ('checkup',)

    # def checkup_title(self, obj):
    #     if obj.checkup.title:
    #         return obj.checkup.title
    #     else:
    #         return ""


@admin.register(PatientDrug)
class PatientDrugAdmin(admin.ModelAdmin):
    list_display = ("patient", "drug", "amount", "instruction", )
    # list_filter = ("checkup", "questionShare", "questionOption",)
    # search_fields = ('checkup',)

    # def checkup_title(self, obj):
    #     if obj.checkup.title:
    #         return obj.checkup.title
    #     else:
    #         return ""


@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "created_on")
    list_filter = ("title", "created_on",)
    search_fields = ('title',)


@admin.register(ClinicInfo)
class ClinicInfoAdmin(admin.ModelAdmin):
    list_display = ("clinic", "name", "showState", "priority", "description", "created_on")
    list_filter = ("created_on", "clinic", "showState", "priority", "description",)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(RealClinic)
class RealClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "address", "icon", "showState", "priority", "long", "lat", "created_on",)
    list_filter = ("address",)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(RealDoctor)
class RealDoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialyTitle", "description", "address", "icon", "showState", "priority", "long", "lat", "created_on",)
    list_filter = ("address",)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Checkup)
class CheckupAdmin(admin.ModelAdmin):
    list_display = ("pk", "patientProfile", "clinic", "executionDate", "clinic_checkup", "title",)
    list_filter = ("clinic", "executionDate")
    search_fields = ('patientProfile',)
    ordering = ('-executionDate',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("clinic", "title", "description", "severity", "reminder_time_scale", "reminder_number", "reminder_type")
    search_fields = ('title',)
    ordering = ('-created_on',)


# @admin.register(QuestionInputType)
# class QuestionInputTypeAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_on")
#     list_filter = ("created_on",)
#     search_fields = ('title',)
#     ordering = ('-created_on',)
#
#
# @admin.register(QuestionFormatType)
# class QuestionFormatTypeAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_on")
#     list_filter = ("created_on",)
#     search_fields = ('title',)
#     ordering = ('-created_on',)
#
#
# @admin.register(QuestionGroup)
# class QuestionGroupAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_on")
#     list_filter = ("created_on",)
#     search_fields = ('title',)
#     ordering = ('-created_on',)
#
#
# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_on", "questionGroup", "questionType", "questionInputType", "inputMaskFormat", "betweenRanges", "description")
#     list_filter = ("created_on", "questionGroup", "questionType", "questionInputType", "inputMaskFormat", "betweenRanges", "description")
#     search_fields = ('title',)
#     ordering = ('-created_on',)
#
#
# @admin.register(QuestionDefultItem)
# class QuestionDefultItemAdmin(admin.ModelAdmin):
#     list_display = ("value", "priority", "question", "created_on")
#     list_filter = ("priority", "created_on", "question",)
#     search_fields = ('value',)
#     ordering = ('-created_on',)
#
#
# @admin.register(Answer)
# class AnswerAdmin(admin.ModelAdmin):
#     list_display = ("value", "checkup", "question", "created_on", "isValueTF", "valueTF")
#     list_filter = ("checkup", "created_on", "question",)
#     search_fields = ('value',)
#     ordering = ('-created_on',)
#
#
# @admin.register(ClinicQuestion)
# class ClinicQuestionAdmin(admin.ModelAdmin):
#     list_display = ("clinic", "question", "created_on")
#     list_filter = ("clinic", "created_on", "question",)
#     # search_fields = ('',)
#     ordering = ('-created_on',)
