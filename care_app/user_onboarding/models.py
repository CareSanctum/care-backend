from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, email=None, password=None, role="USERS"):
        if not phone:
            raise ValueError("Phone number is required")

        username = email.split("@")[0] if email else f"user_{uuid.uuid4().hex[:8]}"

        user = self.model(phone=phone, email=self.normalize_email(email), username=username, role=role)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone, email=None, password=None):
        user = self.create_user(phone, email, password, role="ADMIN")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("USERS", "Users"),
        ("USER_KIN", "User Kin"),
        ("CARE_MANAGER", "Care Manager"),
        ("ADMIN", "Admin"),
        ("ENG_TEAM", "Engineering Team"),
    ]

    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USERS")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
