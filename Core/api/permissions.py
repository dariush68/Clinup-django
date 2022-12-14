from rest_framework import permissions
from Core.models import Supervisor


# For using in ViewSets which have "User" directly
class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# For using in PatientProfileViewSet
class IsPatientSupervisor(permissions.BasePermission):
    """
    Object-level permission to only allow patient or its supervisor to edit itself object.
    """

    def has_object_permission(self, request, view, obj):
        try:
            return obj.user == request.user or obj.supervisor_patient.user == request.user
        except Supervisor.DoesNotExist:
            return obj == request.user


# For using in PatientProfileViewSet
class IsSupervisorOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners(patient or user) of a Supervisor object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or obj.patient.user == request.user


# Only for using in UserViewSet
class IsUserOwnerOrSupervisor(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        try:
            return obj == request.user or obj.patient_user.supervisor_patient.user == request.user
        except Supervisor.DoesNotExist:
            return obj == request.user


# Only for using in ClinicViewSet
class IsClinicOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.agent.user == request.user


# Only for using in ClinicMediaViewSet and ClinicInfoViewSet
class IsClinicMediaAndInfoOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.clinic.agent.user == request.user


# Only for using in CheckupViewSet
class IsCheckupOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.patientProfile.user == request.user


# Only for using in QuestionShareViewSet and CompressedQuestionShareViewSet
class IsQuestionShareOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.doctor.user == request.user


# Only for using in QuestionOptionViewSet and QuestionOrganViewSet (Also usable in QuestionShareMediaViewSet)
class IsQuestionOptionAndOrganOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.questionShare.doctor.user == request.user


# Only for using in QuestionOptionNumberViewSet, QuestionOptionEquationViewSet and QuestionOptionDateViewSet
class IsQuestionOptionNumEqDatOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.questionOption.questionShare.doctor.user == request.user


# Only for using in QuestionAnswerViewSe
class IsQuestionAnswerOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.checkup.patientProfile.user == request.user


class IsCreationOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.user.is_anonymous:
            if view.action == 'create':
                return True
            else:
                return False

        if not request.user.is_authenticated:
            if view.action == 'create':
                return True
            else:
                return False
        else:
            return True
