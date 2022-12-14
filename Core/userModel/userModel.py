# Guid url: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    if value and is_number(value) and \
            is_valid_phone_number(value) and \
            len(value) == 11:
        return value
    else:
        raise ValidationError("لطفا یک شماره همراه معتبر وارد کنید.")


def validate_landline(value):
    if value and is_number(value) and \
            is_valid_landline(value) and \
            len(value) == 11:
        return value
    else:
        raise ValidationError("لطفا یک شماره تلفن ثابت معتبر وارد کنید.")


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_valid_phone_number(number):
    if number[0] == '0' and number[1] == '9':
        return True
    else:
        return False


def is_valid_landline(number):
    if number[0] == '0':
        return True
    else:
        return False


def validate_image(image):
    min_height = 200
    min_width = 200
    height = image.height
    width = image.width
    if width < min_width or height < min_height:
        raise ValidationError("سایز عکس باید از 200 * 200 بیشتر باشد!")


class UserManager(BaseUserManager):

    def _create_user(self, phone_number, password, **extra_fields):
        """Create and save a new user"""
        if phone_number and \
                is_number(phone_number) and \
                is_valid_phone_number(phone_number) and \
                len(phone_number) == 11:
            pass
        else:
            raise ValueError('شماره موبایل معتبر نسیت.')

        user = self.model(
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        # print(f'user saved with {user.phone_number} , {user.password}')

        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        """create and save new super user"""
        # print(f'create superuser {phone_number} {password}')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)

