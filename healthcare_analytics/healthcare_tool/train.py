import os
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

# Ensure the ml_models directory exists
if not os.path.exists('ml_models'):
    os.makedirs('ml_models')

# ----- Bed Model -----
# Load the historical beds data
bed_csv = r'C:\Users\Administrator\Desktop\Healthcare_Tool\healthcare_analytics\healthcare_tool\historical_beds.csv'
bed_data = pd.read_csv(bed_csv)

# Features: allocated_beds and total_beds
X_beds = bed_data[['allocated_beds', 'total_beds']]
# Target: future_beds_required
y_beds = bed_data['future_beds_required']

# Train a Linear Regression model for predicting future bed requirements
bed_model = LinearRegression()
bed_model.fit(X_beds, y_beds)

# Save the bed model as a .pkl file
joblib.dump(bed_model, 'bed_model.pkl')
print("Bed model trained and saved as bed_model.pkl")

# ----- Staff Model -----
# Load the historical staff data
staff_csv = r'C:\Users\Administrator\Desktop\Healthcare_Tool\healthcare_analytics\healthcare_tool\historical_staff.csv'
staff_data = pd.read_csv(staff_csv)

# Features: total_doctors and total_nurses
X_staff = staff_data[['total_doctors', 'total_nurses']]
# Target: future_staff_required
y_staff = staff_data['future_staff_required']

# Train a Linear Regression model for predicting future staff requirements
staff_model = LinearRegression()
staff_model.fit(X_staff, y_staff)

# Save the staff model as a .pkl file
joblib.dump(staff_model, 'staff_model.pkl')
print("Staff model trained and saved as ml_models/staff_model.pkl")
