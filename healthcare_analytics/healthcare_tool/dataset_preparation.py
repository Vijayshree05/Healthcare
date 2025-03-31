import os
import numpy as np
import pandas as pd

# Set a random seed for reproducibility
np.random.seed(42)

# Number of data points to generate
num_rows = 50

# --- Generate historical_beds.csv ---
# allocated_beds: random integers between 5 and 15
allocated_beds = np.random.randint(5, 16, size=num_rows)
# total_beds: allocated_beds + random extra beds (between 5 and 15)
total_beds = allocated_beds + np.random.randint(5, 16, size=num_rows)
# future_beds_required: allocated_beds + a small random increment (between 1 and 5)
future_beds_required = allocated_beds + np.random.randint(1, 6, size=num_rows)

bed_data = pd.DataFrame({
    'allocated_beds': allocated_beds,
    'total_beds': total_beds,
    'future_beds_required': future_beds_required
})

bed_csv = 'historical_beds.csv'
bed_data.to_csv(bed_csv, index=False)
print(f"Generated {num_rows} rows for {bed_csv}")

# --- Generate historical_staff.csv ---
# total_doctors: random integers between 5 and 15
total_doctors = np.random.randint(5, 16, size=num_rows)
# total_nurses: random integers between 10 and 25
total_nurses = np.random.randint(10, 26, size=num_rows)
# future_staff_required: sum of doctors and nurses plus a random adjustment between -2 and 5
future_staff_required = total_doctors + total_nurses + np.random.randint(-2, 6, size=num_rows)

staff_data = pd.DataFrame({
    'total_doctors': total_doctors,
    'total_nurses': total_nurses,
    'future_staff_required': future_staff_required
})

staff_csv = 'historical_staff.csv'
staff_data.to_csv(staff_csv, index=False)
print(f"Generated {num_rows} rows for {staff_csv}")
