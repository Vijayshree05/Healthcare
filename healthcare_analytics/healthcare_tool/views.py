import matplotlib.pyplot as plt
import joblib
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Bed, Department,Patient,Nurse
import joblib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, Doctor, Nurse, Department, Bed, Revenue
from .forms import CustomUserForm
# Admin dashboard with machine learning predictions
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Bed, Doctor, Nurse, Revenue, Department, Patient
import joblib
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Revenue, Bed, Doctor, Department
import joblib
import os
import json
import pandas as pd


# Home page
def home(request):
    return render(request, "shopping/index.html")

# User registration
def register(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            if role == 'doctor':
                department = Department.objects.first()  # Ideally, more advanced selection logic here
                if not department:
                    messages.error(request, "No department available. Contact Admin.")
                    return redirect('register')
                Doctor.objects.create(user=user, department=department)
            elif role == 'nurse':
                Nurse.objects.create(user=user)
            elif role == 'receptionist':
                # Receptionists later register patients via their dashboard.
                pass
            elif role == 'admin':
                pass
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserForm()
    return render(request, 'shopping/register.html', {'form': form})

# User login
def login_user(request):
    if request.user.is_authenticated:
        if request.user.role == 'receptionist':
            return redirect('receptionist_dashboard')
        elif request.user.role == 'doctor':
            return redirect('doctor_dashboard')
        elif request.user.role == 'nurse':
            return redirect('nurse_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect("home")
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                if user.role == 'receptionist':
                    return redirect('receptionist_dashboard')
                elif user.role == 'doctor':
                    return redirect('doctor_dashboard')
                elif user.role == 'nurse':
                    return redirect('nurse_dashboard')
                elif user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid Username or Password")
                return redirect("/login")
        return render(request, "shopping/login.html")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out Successfully")
    return redirect("/")

# Receptionist dashboard (for entering patient details)
@login_required
def receptionist_dashboard(request):
    if request.user.role != 'receptionist':
        return redirect('home')
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        symptoms = request.POST.get('symptoms')

        mapping = {
            'Gastroenterology': ['abdominal pain', 'bloating', 'diarrhea', 'constipation', 'heartburn/acid reflux', 'nausea & vomiting', 'blood in stool', 'unexplained weight loss'],
            'Orthology': ['joint pain', 'swelling', 'stiffness', 'limited range of motion', 'bone fractures', 'muscle weakness', 'back pain', 'inflammation'],
            'Cardiology': ['chest pain', 'shortness of breath', 'palpitations', 'fatigue', 'rapid heartbeat', 'high blood pressure', 'fainting', 'cold sweats'],
            'Pediatrics': ['failure to thrive', 'delayed milestones', 'frequent ear infections', 'diaper rash', 'teething pain', 'childhood asthma', 'croup', 'separation anxiety'],
            'Neurology': ['headache', 'dizziness', 'numbness', 'tingling sensation', 'seizures', 'muscle weakness', 'loss of coordination', 'difficulty speaking', 'memory loss'],
            'General': ['sore throat','cold', 'cough', 'sneezing', 'fever', 'itchy eyes', 'swollen lymph nodes']
}        

        best_department = None

        # Ensure symptoms variable is properly formatted (lowercase & split into words)
        symptoms_list = symptoms.lower().split(', ')  # Splitting assuming symptoms are comma-separated

        # Check for department assignment based on *exact word matches*
        for dept_name, keywords in mapping.items():
            for keyword in keywords:
                if keyword in symptoms_list:  # Only match *exact* words
                    try:
                        best_department = Department.objects.get(name__iexact=dept_name)
                        break  # Found a match; break out of the inner loop.
                    except Department.DoesNotExist:
                        continue  # Skip if the department doesn't exist.
            if best_department:
                break  # Stop checking once a department is assigned.

        # If no match was found, default to the first available department.
        if not best_department:
               best_department = Department.objects.first()
        
        # Find an available doctor in the chosen department.
        doctor = Doctor.objects.filter(department=best_department, available=True).first()
        
        # Create the patient record.
        Patient.objects.create(
            name=name,
            age=age,
            gender=gender,
            symptoms=symptoms,
            department=best_department,
            doctor=doctor,
            status='outpatient'
        )
        
        # Optionally mark the doctor as not available.
        if doctor:
            doctor.available = False
            doctor.save()
        
        messages.success(request, "Patient registered successfully")
    return render(request, 'shopping/receptionist_dashboard.html')

# Doctor dashboard
from django.utils import timezone


@login_required
def doctor_dashboard(request):
    """
    Display the doctor's dashboard with the list of patients assigned to them,
    along with the ability to update patient status. When a patient is updated
    to 'inpatient', an available bed in the doctor's department is allocated,
    the patient's admission time is recorded (if not already set), and a revenue
    record is created for treatment expenses. When the status changes to 'outpatient'
    from 'inpatient', the discharge time is recorded.
    """
    # Only allow access for users with the 'doctor' role
    if request.user.role != 'doctor':
        return redirect('home')
    
    doctor = request.user.doctor
    # Get patients assigned to this doctor
    patients = Patient.objects.filter(doctor=doctor)
    # Get available beds in the doctor's department (unoccupied beds)
    available_beds = Bed.objects.filter(department=doctor.department, is_occupied=False)
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        new_status = request.POST.get('status')
        patient = get_object_or_404(Patient, id=patient_id)
        old_status = patient.status  # Capture previous status
        patient.status = new_status
        
        if new_status == 'inpatient':
            # Set admitted_at timestamp if not already set
            if not patient.admitted_at:
                patient.admitted_at = timezone.now()
            # Check for a selected bed from the form
            bed_id = request.POST.get('bed_id')
            if bed_id:
                try:
                    bed = Bed.objects.get(id=bed_id, department=doctor.department, is_occupied=False)
                    bed.is_occupied = True
                    bed.save()
                except Bed.DoesNotExist:
                    messages.error(request, "Selected bed is not available.")
                    return redirect('doctor_dashboard')
            else:
                # If no bed is selected, use the first available bed
                bed = available_beds.first()
                if bed:
                    bed.is_occupied = True
                    bed.save()
                else:
                    messages.error(request, "No available beds in your department.")
                    return redirect('doctor_dashboard')
            # Record a fixed treatment expense for revenue calculation
            Revenue.objects.create(patient=patient, amount=5000)
        elif new_status == 'outpatient':
            # If patient transitions from inpatient to outpatient, record discharge time if not set
            if old_status == 'inpatient' and not patient.discharged_at:
                patient.discharged_at = timezone.now()
        
        patient.save()
        messages.success(request, "Patient status updated successfully.")
        return redirect('doctor_dashboard')
    
    context = {
        'patients': patients,
        'available_beds': available_beds,
    }
    return render(request, 'shopping/doctor_dashboard.html', context)



# Nurse dashboard (for updating patient details including medication)
@login_required
def nurse_dashboard(request):
    if request.user.role != 'nurse':
        return redirect('home')
    patients = Patient.objects.all()
    return render(request, 'shopping/nurse_dashboard.html', {'patients': patients})



@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':  # Ensure only admin users can access
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Load the trained model
    model_path = r"C:\Users\WELCOME\OneDrive\Desktop\Healthcare_Tool\healthcare_analytics\healthcare_tool\ml_models\bed_model.pkl"
    try:
        bed_model = joblib.load(model_path)
    except Exception as e:
        return JsonResponse({"error": f"Failed to load model: {str(e)}"})

    # Get user inputs from request
    department_id = request.GET.get('department')
    num_days = int(request.GET.get('days', 7))  # Default to 7 days if not provided
    selected_department = None

    if department_id:
        try:
            selected_department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({"error": "Invalid department selected"})

    # Get bed data for the selected department
    if selected_department:
        total_patients = Patient.objects.filter(department=selected_department).count()
        total_beds = Bed.objects.filter(department=selected_department).count()
        total_doctors = Doctor.objects.filter(department=selected_department).count()
        occupied_beds = Bed.objects.filter(is_occupied=True, department=selected_department).count()
        total_nurses = Nurse.objects.count() 
    else:
        total_beds = Bed.objects.count()
        occupied_beds = Bed.objects.filter(is_occupied=True).count()
        total_doctors = Doctor.objects.count()
        total_patients = Patient.objects.count()
        total_nurses = Nurse.objects.count() 
    # Predict future bed occupancy
    future_dates = pd.date_range(start=pd.Timestamp.today(), periods=num_days)
    future_days_of_year = future_dates.dayofyear
    future_X_beds = pd.DataFrame({'DayOfYear': future_days_of_year, 'TotalBeds': [total_beds] * num_days})
    
    future_predictions_beds = bed_model.predict(future_X_beds)

    # Estimate staff requirements (assuming 1 staff per 3 occupied beds)
    future_predictions_staff = (future_predictions_beds / 3).round(0).astype(int)

    # Save predictions for display
    df_future = pd.DataFrame({
        'Date': future_dates,
        'PredictedBedsOccupied': future_predictions_beds.round(0).astype(int),
        'PredictedStaffRequired': future_predictions_staff
    })

    # Ensure 'static/images/' directory exists before saving the plot
    plot_dir = r"C:\Users\WELCOME\OneDrive\Desktop\Healthcare_Tool\healthcare_analytics\static"
    os.makedirs(plot_dir, exist_ok=True)  # Create directory if it doesn't exist
    plot_path = os.path.join(plot_dir, "bed_prediction.png")

    # Plot results
    plt.figure(figsize=(10, 5))
    plt.plot(df_future['Date'], df_future['PredictedBedsOccupied'], marker='o', linestyle='-', color='b', label='Beds')
    plt.plot(df_future['Date'], df_future['PredictedStaffRequired'], marker='s', linestyle='-', color='r', label='Staff')
    plt.xlabel("Date")
    plt.ylabel("Predicted Values")
    plt.title(f"Predicted Bed and Staff Requirement ({num_days} Days)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.savefig(plot_path)
    plt.close()

    context = {
        'allocated_beds': occupied_beds,
        'total_beds': total_beds,
       # 'future_beds_required': int(future_predictions_beds[-1]),
        'total_doctors':total_doctors,
        'total_patients':total_patients,
        'total_nurses':total_nurses,
        'departments': Department.objects.all(),
        'selected_department': selected_department,
        'days': num_days,
        'plot_path': plot_path
    }

    return render(request, 'shopping/admin_dashboard.html', context)
@login_required
def update_medication(request, patient_id):
    if request.user.role != 'nurse':
        return redirect('home')
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        new_medication = request.POST.get('medication')
        patient.medication = new_medication
        patient.save()
        messages.success(request, "Medication updated successfully")
        return redirect('nurse_dashboard')
    return render(request, 'shopping/update_medication.html', {'patient': patient})


@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    # Here you can also retrieve treatment history or other details if needed.
    return render(request, 'shopping/patient_detail.html', {'patient': patient})


from .forms import BedForm
from .models import Bed

@login_required
def create_bed(request):
    # Only admin can create new beds
    if request.user.role != 'admin':
        return redirect('home')

    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New bed created successfully!")
            return redirect('bed_list')  # or wherever you want to go after creation
    else:
        form = BedForm()
    
    return render(request, 'shopping/create_bed.html', {'form': form})

@login_required
def bed_list(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    beds = Bed.objects.all().order_by('department')
    return render(request, 'shopping/bed_list.html', {'beds': beds})

from .forms import DoctorDepartmentForm

@login_required
def doctor_list(request):
    # Only admin can manage doctor departments.
    if request.user.role != 'admin':
        return redirect('home')
    doctors = Doctor.objects.all()
    return render(request, 'shopping/doctor_list.html', {'doctors': doctors})

@login_required
def update_doctor_department(request, doctor_id):
    # Only admin can update doctor departments.
    if request.user.role != 'admin':
        return redirect('home')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        form = DoctorDepartmentForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor's department updated successfully.")
            return redirect('doctor_list')
    else:
        form = DoctorDepartmentForm(instance=doctor)
    return render(request, 'shopping/update_doctor_department.html', {'form': form, 'doctor': doctor})