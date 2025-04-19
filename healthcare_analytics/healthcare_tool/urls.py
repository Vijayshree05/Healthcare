from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # User Registration
    path('register/', views.register, name='register'),
    
    # User Login
    path('login/', views.login_user, name='login'),
    
    # Receptionist Dashboard
    path('receptionist/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),

    # Doctor Dashboard
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    # Nurse Dashboard
    path('nurse/dashboard/', views.nurse_dashboard, name='nurse_dashboard'),

    
    # Admin Dashboard
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    
    path('beds/', views.beds_detail, name='beds_detail'),
    path('occupied/', views.occupied_beds_detail, name='occupied_beds_detail'),
    path('doctors/', views.doctors_detail, name='doctors_detail'),
    path('patients/', views.patients_detail, name='patients_detail'),
    path('nurses/', views.nurses_detail, name='nurses_detail'),

    path('logout/', views.logout_page, name='logout'),  # Uncomment if you implement a logout view
    path('update_medication/<int:patient_id>/', views.update_medication, name='update_medication'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),

    path('admin_dashboard/create_bed/', views.create_bed, name='create_bed'),
    path('admin_dashboard/beds/', views.bed_list, name='bed_list'),

    path('admin_dashboard/doctors/', views.doctor_list, name='doctor_list'),
    path('admin_dashboard/doctors/update/<int:doctor_id>/', views.update_doctor_department, name='update_doctor_department'),
]
