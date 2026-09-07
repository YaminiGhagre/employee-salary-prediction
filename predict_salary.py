import joblib
import mysql.connector
import pandas as pd

# Load trained ML model
model = joblib.load("model/salary_model.pkl")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@789",
    database="employee_salary_db"
)

cursor = conn.cursor(dictionary=True)

# Get one employee from MySQL
employee_id = int(input("Enter Employee ID: "))

query = """
SELECT 
    e.employee_id,
    e.age,
    e.gender,
    e.education,
    e.experience_years,
    e.job_title,
    e.department,
    e.location,
    e.employment_type,
    p.performance_rating,
    p.projects_completed,
    p.overtime_hours,
    p.skills_count
FROM employees e
JOIN employee_performance p
ON e.employee_id = p.employee_id
WHERE e.employee_id = %s
"""

cursor.execute(query, (employee_id,))
employee = cursor.fetchone()

if employee is None:
    print("Employee not found.")
else:
    # Convert database record to DataFrame
    input_data = pd.DataFrame([employee])

    # Remove ID because it is not an ML feature
    input_data = input_data.drop(columns=["employee_id"])

    # Predict salary
    predicted_salary = model.predict(input_data)[0]

    print("\nEmployee found!")
    print("Employee ID:", employee_id)
    print(f"Predicted Salary: ₹{predicted_salary:,.2f}")

    # Store prediction in MySQL
    insert_query = """
    INSERT INTO salary_predictions
    (employee_id, predicted_salary, model_name)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        insert_query,
        (employee_id, float(predicted_salary), "Random Forest")
    )

    conn.commit()

    print("Prediction saved to MySQL.")

cursor.close()
conn.close()