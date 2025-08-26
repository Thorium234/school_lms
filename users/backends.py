from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

try:
    from library.models import Student
except ImportError:
    Student = None

class StudentAuthBackend(ModelBackend):
    """
    Authenticate students using first_name and admission_number.
    """
    def authenticate(self, request, first_name=None, admission_number=None, **kwargs):
        if not (first_name and admission_number):
            return None
        UserModel = get_user_model()
        try:
            profile = UserModel.objects.get(profile__admission_number=admission_number, first_name__iexact=first_name)
            if profile.profile.role == 'student':
                return profile
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

class StaffAuthBackend(ModelBackend):
    """
    Staff can login with username/email/phone.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) |
                Q(email__iexact=username) |
                Q(profile__phone__iexact=username)
            )
            if user.check_password(password) and user.profile.role in ['admin', 'staff', 'super_admin']:
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

class EmailBackend(ModelBackend):
    """
    Authenticate using email address (case insensitive)
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None