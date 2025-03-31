from django.contrib.auth.models import AbstractUser
from django.db import models

# User model with role-based access
class User(AbstractUser):
    ROLE_CHOICES = [
        ('receptionist', 'Receptionist'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Add related_name to avoid clash with the default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='healthcare_tool_user_set',  # Changed to avoid clash
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='healthcare_tool_user_permissions',  # Changed to avoid clash
        blank=True
    )


# Department model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Doctor model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.username} - {self.department.name}"


# Patient model
class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    symptoms = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('inpatient', 'In-Patient'), ('outpatient', 'Out-Patient')]
    )
    admitted_at = models.DateTimeField(null=True, blank=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    # Add medication field
    medication = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return self.name



# Nurse model
class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# Bed model
class Bed(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Bed in {self.department.name} - {'Occupied' if self.is_occupied else 'Available'}"


# Revenue model
class Revenue(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revenue for {self.patient.name}: {self.amount}"
