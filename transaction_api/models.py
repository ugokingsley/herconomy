from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
#from axes.models import AccessAttempt
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tier(models.Model):
    tier_name = models.CharField(max_length=140, blank=True, null=True)
    amount = models.DecimalField(max_digits=50, default=0, decimal_places=1)

    def __str__(self):
        return str(self.tier_name)
                
    class Meta:
        ordering = ["-pk"]

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = models.CharField(blank=True, null=True, default=None, max_length=140)
    email = models.EmailField(unique=True, blank=True, default=None)
    account_balance = models.DecimalField(max_digits=50, default=0, decimal_places=1)
    transaction_tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, blank=True,null=True)
    last_transaction_time = models.DateTimeField(auto_now=True)
    flagged = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        
    def __str__(self):
        return str(self.email)
                
    class Meta:
        ordering = ["-pk"]


class AccessAttempt(models.Model):
    user = models.EmailField(null=True)
    attempt_count = models.IntegerField(default=0)
    time_last_unsuccessful_login = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.user)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True,null=True)
    transaction_type = models.CharField(max_length=140, blank=True, null=True)
    transaction_ref = models.CharField(max_length=140, blank=True, null=True)
    amount = models.DecimalField(max_digits=50, default=0, decimal_places=1)
    narration = models.CharField(max_length=140, blank=True, null=True)
    payment_at = models.DateTimeField(auto_now_add=True)
    device_signature = models.CharField(max_length=140, blank=True, null=True)
    ip_address = models.CharField(max_length=140, blank=True, null=True)

    def __str__(self):
        return str(self.user)
                
    class Meta:
        ordering = ["-pk"]

