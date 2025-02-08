from django.urls import path
from .views import RegisterView, LoginView, CreateOrUpdatePatientData, UserDetailsView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("add_patient_data/", CreateOrUpdatePatientData.as_view(), name="add_patient_data"),
    path("user-details/<str:username>/", UserDetailsView.as_view(), name="user-details"),
]
