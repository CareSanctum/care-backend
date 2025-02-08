from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, role="USERS"):
        if not phone_number and not email:
            raise ValueError("Users must have a phone number or email")
        if not password:
            raise ValueError("Users must have a password")

        username = email.split("@")[0] if email else f"user_{uuid.uuid4().hex[:8]}"
        user = self.model(phone_number=phone_number, email=self.normalize_email(email), username=username, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None):
        user = self.create_user(phone_number, email, password, role="ADMIN")
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

    phone_number = models.CharField(max_length=15, unique=True, blank=True,null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USERS")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username


# Patient-related models
class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="patient_profile")
    dob = models.DateField(verbose_name="Date of Birth")
    full_name = models.CharField(max_length=100, null=True, blank=True) 
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    address = models.TextField(verbose_name="Address")
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    height = models.PositiveIntegerField(help_text="Height in cm")
    weight = models.PositiveIntegerField(help_text="Weight in kg")
    id_proof = models.FileField(upload_to='id_proofs/',null=True)
    profile_picture = models.FileField(upload_to='profile_pic/',null=True)
    usual_wake_up_time = models.TimeField()
    current_location_status = models.CharField(max_length=50, choices=[('AtHome', 'At Home'), ('Travelling', 'Travelling')])
    expected_return_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)  # Removed unique constraint
    alternate_phone = models.CharField(max_length=15, blank=True)  # Removed unique constraint
    pin_code = models.CharField(max_length=15, blank=True)  # Removed unique constraint

    def __str__(self):
        return f"Patient Profile of {self.user.username}"


class EmergencyContact(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="emergency_contacts")  # Changed to ForeignKey
    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_contact_number = models.CharField(max_length=15)
    relationship_with_senior = models.CharField(max_length=50)
    neighbor_name = models.CharField(max_length=100, null=True, blank=True)
    neighbor_contact_number = models.CharField(max_length=15, null=True, blank=True)


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_histories")  # Changed related_name
    existing_health_conditions = models.TextField(null=True, blank=True, help_text="List any chronic illnesses")
    known_allergies = models.TextField(null=True, blank=True, help_text="Food, medication, environmental allergies")
    current_prescriptions = models.FileField(upload_to='prescriptions/', null=True, blank=True)
    past_surgeries = models.TextField(null=True, blank=True, help_text="Include dates if available")


class PreferredMedicalServices(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="preferred_medical_services")  # Changed related_name
    preferred_doctor_name = models.CharField(max_length=100, null=True, blank=True)
    doctor_contact_number = models.CharField(max_length=15, null=True, blank=True)
    preferred_hospital_or_clinic = models.CharField(max_length=100, null=True, blank=True)


class LifestyleDetails(models.Model):
    ACTIVITY_LEVEL_CHOICES = [
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High')
    ]
    DIET_PREFERENCES_CHOICES = [
        ('Vegetarian', 'Vegetarian'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
        ('Vegan', 'Vegan'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="lifestyle_details")  # Changed related_name
    activity_level = models.CharField(max_length=10, choices=ACTIVITY_LEVEL_CHOICES, null=True, blank=True)
    diet_preferences = models.CharField(max_length=15, choices=DIET_PREFERENCES_CHOICES, null=True, blank=True)
    requires_mobility_assistance = models.BooleanField(default=False)
    has_vision_impairment = models.BooleanField(default=False)
    has_hearing_impairment = models.BooleanField(default=False)
