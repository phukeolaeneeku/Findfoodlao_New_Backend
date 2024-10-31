from django.db import models
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CheckEmailQuerySet(models.QuerySet):
    """
    Class required to delete authentication number
    """

    def expired(self):
        return self.filter(expires_at__lt=timezone.now())

    def delete_expired(self):
        self.expired().delete()
        
class CheckEmail(models.Model):
    class Meta:
        verbose_name_plural = "2. Authentication code management"

    email = models.EmailField("Email for verification", max_length=100)
    code = models.CharField("code for confirmation", max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    objects = CheckEmailQuerySet.as_manager()

    def __str__(self):
        return self.email

    def save(self, **kwargs):
        self.expires_at = timezone.now() + timedelta(minutes=3)
        super().save(**kwargs)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, nickname=None):
        if not email:
            raise ValueError("Users must have an email")

        user = self.model(email=email, nickname=nickname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.is_seller = True
        user.is_restaurant = True
        user.is_employee_of_restaurant = True
        user.save(using=self._db)
        return user

class UserModel(AbstractBaseUser):
    class Meta:
        verbose_name_plural = "1. User information"

    email = models.EmailField(verbose_name="Email Address", max_length=100, unique=True)
    nickname = models.CharField(
        verbose_name="nickname", max_length=30, null=True, blank=True
    )
    
    profile_image = models.FileField(
        verbose_name="profile image", null=True, blank=True, upload_to="media/"
    )
    
    password = models.CharField(verbose_name="password", max_length=128)

    is_seller = models.BooleanField(default=False, verbose_name="Seller")
    
    is_restaurant = models.BooleanField(default=False, verbose_name="Restaurant")
    
    is_employee_of_restaurant = models.BooleanField(default=False, verbose_name="Employee of Restaurant")

    is_active = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False, verbose_name="Administrator")

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


