// dashboard_charts.js

// Parse the JSON data passed from the template.
const bedData = JSON.parse(document.getElementById("bed-data").textContent);
const staffData = JSON.parse(document.getElementById("staff-data").textContent);

// Bed Chart
var ctx1 = document.getElementById('bedChart').getContext('2d');
var bedChart = new Chart(ctx1, {
  type: 'bar',
  data: {
    labels: ['Allocated Beds', 'Total Beds', 'Predicted'],
    datasets: [{
      label: 'Bed Stats',
      data: bedData,  // [allocated_beds, total_beds, future_beds_required]
      backgroundColor: ['#FF5733', '#33FF57', '#3357FF']
    }]
  }
});

// Staff Chart
var ctx2 = document.getElementById('staffChart').getContext('2d');
var staffChart = new Chart(ctx2, {
  type: 'line',
  data: {
    labels: ['Doctors', 'Nurses', 'Predicted Staff'],
    datasets: [{
      label: 'Staff Stats',
      data: staffData,  // [total_doctors, total_nurses, predicted_staff_required]
      borderColor: '#FF5733',
      fill: false
    }]
  }
});
