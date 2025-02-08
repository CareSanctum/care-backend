from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        return Response({
            "refresh": str(token),
            "access": str(token.access_token),
            "user_name" : str(user.username)
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data.get("identifier")  # Email or phone
        password = serializer.validated_data.get("password")

        # Find user by email or phone number
        user = CustomUser.objects.filter(email=identifier).first() or CustomUser.objects.filter(phone_number=identifier).first()

        if user is None or not user.check_password(password):
            return Response({"error": "Invalid email/phone number or password"}, status=status.HTTP_401_UNAUTHORIZED)

        token = RefreshToken.for_user(user)
        return Response({
            "refresh": str(token),
            "access": str(token.access_token),
            "user_name" : str(user.username)
        }, status=status.HTTP_200_OK)


class CreateOrUpdatePatientData(APIView):
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get user
        user = get_object_or_404(CustomUser, username=username)

        # 1. Patient (Handling File Upload for id_proof)
        patient_data = request.data.get("patient", {})
        if "id_proof" in request.FILES:  # Check if file is uploaded
            patient_data["id_proof"] = request.FILES["id_proof"]

        if "profile_picture" in request.FILES:  # Check if file is uploaded
            patient_data["profile_picture"] = request.FILES["profile_picture"]

        patient, _ = Patient.objects.update_or_create(
            user=user,
            defaults=patient_data
        )

        # 2. Emergency Contacts
        emergency_contacts = request.data.get("emergency_contacts", [])
        for contact_data in emergency_contacts:
            EmergencyContact.objects.update_or_create(
                patient=patient,
                next_of_kin_contact_number=contact_data.get("next_of_kin_contact_number"),
                defaults=contact_data
            )

        # 3. Medical History (Handling File Upload for current_prescriptions)
        medical_history_data = request.data.get("medical_history", {})
        if "current_prescriptions" in request.FILES:  # Check if file is uploaded
            medical_history_data["current_prescriptions"] = request.FILES["current_prescriptions"]

        MedicalHistory.objects.update_or_create(
            patient=patient,
            defaults=medical_history_data
        )

        # 4. Preferred Medical Services
        preferred_services_data = request.data.get("preferred_medical_services", {})
        PreferredMedicalServices.objects.update_or_create(
            patient=patient,
            defaults=preferred_services_data
        )

        # 5. Lifestyle Details
        lifestyle_details_data = request.data.get("lifestyle_details", {})
        LifestyleDetails.objects.update_or_create(
            patient=patient,
            defaults=lifestyle_details_data
        )

        return Response({"message": "Records successfully added/updated"}, status=status.HTTP_201_CREATED)
    

class UserDetailsView(APIView):
    """
    API to fetch all user details based on the username.
    """
    def get(self, request, username):
        # Fetch User
        user = get_object_or_404(CustomUser, username=username)
        
        # Fetch Related Data
        patient = Patient.objects.filter(user=user).first()
        emergency_contacts = EmergencyContact.objects.filter(patient=patient)
        medical_history = MedicalHistory.objects.filter(patient=patient).first()
        preferred_services = PreferredMedicalServices.objects.filter(patient=patient).first()
        lifestyle_details = LifestyleDetails.objects.filter(patient=patient).first()
        
        # Serialize Data
        response_data = {
            "username": user.username,
            "patient": PatientSerializer(patient).data if patient else None,
            "emergency_contacts": EmergencyContactSerializer(emergency_contacts, many=True).data,
            "medical_history": MedicalHistorySerializer(medical_history).data if medical_history else None,
            "preferred_medical_services": PreferredMedicalServicesSerializer(preferred_services).data if preferred_services else None,
            "lifestyle_details": LifestyleDetailsSerializer(lifestyle_details).data if lifestyle_details else None
        }

        return Response(response_data, status=status.HTTP_200_OK)